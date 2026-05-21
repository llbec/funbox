use std::{
    env,
    error::Error,
    fmt, fs,
    io::{self, Write},
    path::{Path, PathBuf},
    process::Command,
    time::Duration,
};

use expectrl::{Any, Eof, Expect, Regex, session::OsSession, stream::stdin::Stdin};
use serde::Deserialize;

const DEFAULT_SERVER_FILE: &str = "servers.json";

#[derive(Debug, Clone)]
struct Server {
    host: String,
    port: u16,
    username: String,
    use_key: bool,
    secret: String,
    description: String,
}

#[derive(Debug, Deserialize)]
struct ServerConfig {
    host: String,
    #[serde(default = "default_ssh_port")]
    port: u16,
    #[serde(default)]
    user: Option<String>,
    use_key: bool,
    password: Option<String>,
    key_path: Option<String>,
    description: String,
}

#[derive(Debug)]
struct ConfigError(String);

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl Error for ConfigError {}

fn main() {
    if let Err(err) = run() {
        eprintln!("error: {err}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn Error>> {
    let config_path = env::args()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(default_config_path);

    let servers = read_servers(&config_path)?;
    let selected = select_server(&servers)?;

    println!(
        "Connecting to {}@{}:{} ({})",
        selected.username, selected.host, selected.port, selected.description
    );

    login(selected)
}

fn default_config_path() -> PathBuf {
    env::current_exe()
        .ok()
        .and_then(|path| path.parent().map(|parent| parent.join(DEFAULT_SERVER_FILE)))
        .unwrap_or_else(|| PathBuf::from(DEFAULT_SERVER_FILE))
}

fn read_servers(path: &Path) -> Result<Vec<Server>, Box<dyn Error>> {
    let content = fs::read_to_string(path).map_err(|err| {
        ConfigError(format!(
            "failed to open server file '{}': {err}",
            path.display()
        ))
    })?;
    let configs: Vec<ServerConfig> = serde_json::from_str(&content).map_err(|err| {
        ConfigError(format!(
            "failed to parse JSON server file '{}': {err}",
            path.display()
        ))
    })?;

    let servers = configs
        .into_iter()
        .enumerate()
        .map(|(index, config)| Server::try_from_config(index + 1, config))
        .collect::<Result<Vec<_>, _>>()?;
    if servers.is_empty() {
        return Err(Box::new(ConfigError(format!(
            "no server entries found in '{}'",
            path.display()
        ))));
    }

    Ok(servers)
}

impl Server {
    fn try_from_config(index: usize, config: ServerConfig) -> Result<Self, Box<dyn Error>> {
        let username = match config.user {
            Some(user) if !user.trim().is_empty() => user,
            _ => env::var("USER")
                .or_else(|_| env::var("USERNAME"))
                .map_err(|_| {
                    ConfigError(format!("server #{index}: missing user and USER is not set"))
                })?,
        };
        let secret = if config.use_key {
            required_field(index, "key_path", config.key_path)?
        } else {
            required_field(index, "password", config.password)?
        };

        Ok(Self {
            host: required_field(index, "host", Some(config.host))?,
            port: config.port,
            username: username.trim().to_string(),
            use_key: config.use_key,
            secret,
            description: required_field(index, "description", Some(config.description))?,
        })
    }
}

fn default_ssh_port() -> u16 {
    22
}

fn required_field(
    index: usize,
    field_name: &str,
    value: Option<String>,
) -> Result<String, Box<dyn Error>> {
    let value = value.unwrap_or_default();
    let value = value.trim();
    if value.is_empty() {
        return Err(Box::new(ConfigError(format!(
            "server #{index}: {field_name} cannot be empty"
        ))));
    }

    Ok(value.to_string())
}

fn select_server(servers: &[Server]) -> Result<&Server, Box<dyn Error>> {
    println!("Available servers:");
    println!(
        "{:<4} {:<22} {:<7} {:<14} {}",
        "No.", "IP", "Port", "Auth", "Description"
    );

    for (index, server) in servers.iter().enumerate() {
        let auth = if server.use_key { "key" } else { "password" };
        println!(
            "{:<4} {:<22} {:<7} {:<14} {}",
            index + 1,
            server.host,
            server.port,
            auth,
            server.description
        );
    }

    loop {
        print!("Select server number: ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        match input.trim().parse::<usize>() {
            Ok(number) if (1..=servers.len()).contains(&number) => {
                return Ok(&servers[number - 1]);
            }
            _ => println!("Please enter a number between 1 and {}.", servers.len()),
        }
    }
}

fn login(server: &Server) -> Result<(), Box<dyn Error>> {
    let mut command = Command::new("ssh");
    command
        .arg("-p")
        .arg(server.port.to_string())
        .arg("-o")
        .arg("StrictHostKeyChecking=accept-new")
        .arg("-o")
        .arg("ServerAliveInterval=30");

    if server.use_key {
        command.arg("-i").arg(expand_home(&server.secret));
    } else {
        command
            .arg("-o")
            .arg("PreferredAuthentications=password,keyboard-interactive")
            .arg("-o")
            .arg("PubkeyAuthentication=no")
            .arg("-o")
            .arg("KbdInteractiveAuthentication=yes")
            .arg("-o")
            .arg("NumberOfPasswordPrompts=1");
    }

    command.arg(format!("{}@{}", server.username, server.host));

    let mut session = OsSession::spawn(command)?;

    if !server.use_key {
        send_password_when_prompted(&mut session, server)?;
    }

    let mut stdin = Stdin::open()?;
    session.interact(&mut stdin, io::stdout()).spawn()?;
    stdin.close()?;

    Ok(())
}

fn send_password_when_prompted(
    session: &mut OsSession,
    server: &Server,
) -> Result<(), Box<dyn Error>> {
    session.set_expect_timeout(Some(Duration::from_secs(30)));
    let found = session.expect(Any::boxed(vec![
        Box::new(Regex("(?i)(password|passcode).*: ?")),
        Box::new(Regex("(?i)permission denied")),
        Box::new(Regex(
            "(?i)(connection refused|connection timed out|operation timed out|no route to host|could not resolve hostname)",
        )),
        Box::new(Eof),
    ]))?;

    let mut output = Vec::new();
    output.extend_from_slice(found.before());
    if let Some(matched) = found.get(0) {
        output.extend_from_slice(matched);
    }

    let output_text = String::from_utf8_lossy(&output);
    if output_text.to_ascii_lowercase().contains("password")
        || output_text.to_ascii_lowercase().contains("passcode")
    {
        session.send_line(&server.secret)?;
        return Ok(());
    }

    Err(Box::new(ConfigError(format!(
        "ssh exited before a password prompt was shown for {}@{}:{}\n{}",
        server.username,
        server.host,
        server.port,
        clean_output(&output_text)
    ))))
}

fn clean_output(output: &str) -> String {
    let output = output.trim();
    if output.is_empty() {
        "ssh produced no output".to_string()
    } else {
        output.to_string()
    }
}

fn expand_home(value: &str) -> String {
    if value == "~" {
        return env::var("HOME").unwrap_or_else(|_| value.to_string());
    }

    if let Some(rest) = value.strip_prefix("~/") {
        if let Ok(home) = env::var("HOME") {
            return format!("{home}/{rest}");
        }
    }

    value.to_string()
}
