use std::{
    env,
    error::Error,
    fmt, fs,
    io::{self, Write},
    path::{Path, PathBuf},
    sync::Arc,
};

use crossterm::{
    event::{self, Event, KeyCode, KeyEvent, KeyEventKind, KeyModifiers},
    terminal::{self, disable_raw_mode, enable_raw_mode},
};
use russh::{
    ChannelMsg,
    client::{self, AuthResult, KeyboardInteractiveAuthResponse},
    keys::{PrivateKeyWithHashAlg, load_secret_key, ssh_key},
};
use serde::Deserialize;
use tokio::sync::mpsc;

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

#[tokio::main]
async fn main() {
    if let Err(err) = run().await {
        eprintln!("error: {err}");
        std::process::exit(1);
    }
}

async fn run() -> Result<(), Box<dyn Error>> {
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

    login(selected).await
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

async fn login(server: &Server) -> Result<(), Box<dyn Error>> {
    let config = Arc::new(client::Config::default());
    let mut session = client::connect(config, (server.host.as_str(), server.port), Client).await?;

    authenticate(&mut session, server).await?;

    let mut channel = session.channel_open_session().await?;
    let (cols, rows) = terminal::size().unwrap_or((80, 24));
    channel
        .request_pty(
            false,
            terminal_name().as_str(),
            cols as u32,
            rows as u32,
            0,
            0,
            &[],
        )
        .await?;
    channel.request_shell(true).await?;

    run_interactive_shell(&mut channel).await?;
    session
        .disconnect(russh::Disconnect::ByApplication, "", "English")
        .await?;

    Ok(())
}

struct Client;

impl client::Handler for Client {
    type Error = russh::Error;

    async fn check_server_key(
        &mut self,
        _server_public_key: &ssh_key::PublicKey,
    ) -> Result<bool, Self::Error> {
        Ok(true)
    }
}

async fn authenticate(
    session: &mut client::Handle<Client>,
    server: &Server,
) -> Result<(), Box<dyn Error>> {
    if server.use_key {
        let key = load_secret_key(expand_home(&server.secret), None)?;
        let hash = session.best_supported_rsa_hash().await?.flatten();
        let result = session
            .authenticate_publickey(
                server.username.clone(),
                PrivateKeyWithHashAlg::new(Arc::new(key), hash),
            )
            .await?;
        ensure_auth_success(result, server)?;
    } else {
        let result = session
            .authenticate_password(server.username.clone(), server.secret.clone())
            .await?;
        if !result.success() {
            authenticate_keyboard_interactive(session, server).await?;
        }
    }

    Ok(())
}

async fn authenticate_keyboard_interactive(
    session: &mut client::Handle<Client>,
    server: &Server,
) -> Result<(), Box<dyn Error>> {
    let mut response = session
        .authenticate_keyboard_interactive_start(server.username.clone(), None)
        .await?;

    loop {
        match response {
            KeyboardInteractiveAuthResponse::Success => return Ok(()),
            KeyboardInteractiveAuthResponse::Failure { .. } => {
                return Err(auth_error(server));
            }
            KeyboardInteractiveAuthResponse::InfoRequest { prompts, .. } => {
                let answers = prompts
                    .iter()
                    .map(|_| server.secret.clone())
                    .collect::<Vec<_>>();
                response = session
                    .authenticate_keyboard_interactive_respond(answers)
                    .await?;
            }
        }
    }
}

fn ensure_auth_success(result: AuthResult, server: &Server) -> Result<(), Box<dyn Error>> {
    if result.success() {
        Ok(())
    } else {
        Err(auth_error(server))
    }
}

fn auth_error(server: &Server) -> Box<dyn Error> {
    Box::new(ConfigError(format!(
        "authentication failed for {}@{}:{}",
        server.username, server.host, server.port
    )))
}

async fn run_interactive_shell(
    channel: &mut russh::Channel<client::Msg>,
) -> Result<(), Box<dyn Error>> {
    let _raw_mode = RawMode::enter()?;
    let mut stdout = tokio::io::stdout();
    let (input_tx, mut input_rx) = mpsc::unbounded_channel();
    spawn_input_reader(input_tx);

    loop {
        tokio::select! {
            input = input_rx.recv() => {
                match input {
                    Some(TerminalInput::Bytes(bytes)) => {
                        channel.data_bytes(bytes).await?;
                    }
                    Some(TerminalInput::Resize(cols, rows)) => {
                        channel.window_change(cols as u32, rows as u32, 0, 0).await?;
                    }
                    Some(TerminalInput::Exit) | None => {
                        channel.eof().await?;
                        break;
                    }
                }
            }
            msg = channel.wait() => {
                match msg {
                    Some(ChannelMsg::Data { data }) | Some(ChannelMsg::ExtendedData { data, .. }) => {
                        tokio::io::AsyncWriteExt::write_all(&mut stdout, &data).await?;
                        tokio::io::AsyncWriteExt::flush(&mut stdout).await?;
                    }
                    Some(ChannelMsg::ExitStatus { .. }) | Some(ChannelMsg::ExitSignal { .. }) | Some(ChannelMsg::Eof) | Some(ChannelMsg::Close) | None => {
                        break;
                    }
                    _ => {}
                }
            }
        }
    }

    Ok(())
}

enum TerminalInput {
    Bytes(Vec<u8>),
    Resize(u16, u16),
    Exit,
}

fn spawn_input_reader(tx: mpsc::UnboundedSender<TerminalInput>) {
    std::thread::spawn(move || {
        loop {
            match event::read() {
                Ok(Event::Key(key)) if is_key_press(key) => {
                    if is_local_exit_key(key) {
                        let _ = tx.send(TerminalInput::Exit);
                        break;
                    }

                    if let Some(bytes) = key_event_to_bytes(key) {
                        let _ = tx.send(TerminalInput::Bytes(bytes));
                    }
                }
                Ok(Event::Paste(text)) => {
                    let _ = tx.send(TerminalInput::Bytes(text.into_bytes()));
                }
                Ok(Event::Resize(cols, rows)) => {
                    let _ = tx.send(TerminalInput::Resize(cols, rows));
                }
                Ok(_) => {}
                Err(_) => {
                    let _ = tx.send(TerminalInput::Exit);
                    break;
                }
            }
        }
    });
}

fn is_key_press(key: KeyEvent) -> bool {
    matches!(key.kind, KeyEventKind::Press | KeyEventKind::Repeat)
}

fn is_local_exit_key(key: KeyEvent) -> bool {
    key.modifiers.contains(KeyModifiers::CONTROL) && key.code == KeyCode::Char(']')
}

fn key_event_to_bytes(key: KeyEvent) -> Option<Vec<u8>> {
    let modifiers = key.modifiers;

    match key.code {
        KeyCode::Char(ch) => Some(char_key_to_bytes(ch, modifiers)),
        KeyCode::Enter => Some(vec![b'\r']),
        KeyCode::Tab => Some(vec![b'\t']),
        KeyCode::BackTab => Some(b"\x1b[Z".to_vec()),
        KeyCode::Backspace => Some(vec![0x7f]),
        KeyCode::Delete => Some(b"\x1b[3~".to_vec()),
        KeyCode::Insert => Some(b"\x1b[2~".to_vec()),
        KeyCode::Esc => Some(vec![0x1b]),
        KeyCode::Up => Some(b"\x1b[A".to_vec()),
        KeyCode::Down => Some(b"\x1b[B".to_vec()),
        KeyCode::Right => Some(b"\x1b[C".to_vec()),
        KeyCode::Left => Some(b"\x1b[D".to_vec()),
        KeyCode::Home => Some(b"\x1b[H".to_vec()),
        KeyCode::End => Some(b"\x1b[F".to_vec()),
        KeyCode::PageUp => Some(b"\x1b[5~".to_vec()),
        KeyCode::PageDown => Some(b"\x1b[6~".to_vec()),
        KeyCode::F(number) => function_key_to_bytes(number),
        KeyCode::Null | KeyCode::CapsLock | KeyCode::ScrollLock | KeyCode::NumLock => None,
        KeyCode::PrintScreen | KeyCode::Pause | KeyCode::Menu | KeyCode::KeypadBegin => None,
        KeyCode::Media(_) | KeyCode::Modifier(_) => None,
    }
}

fn char_key_to_bytes(ch: char, modifiers: KeyModifiers) -> Vec<u8> {
    let mut bytes = Vec::new();

    if modifiers.contains(KeyModifiers::ALT) {
        bytes.push(0x1b);
    }

    if modifiers.contains(KeyModifiers::CONTROL) {
        if let Some(control) = control_byte(ch) {
            bytes.push(control);
            return bytes;
        }
    }

    let mut encoded = [0_u8; 4];
    bytes.extend_from_slice(ch.encode_utf8(&mut encoded).as_bytes());
    bytes
}

fn control_byte(ch: char) -> Option<u8> {
    match ch {
        'a'..='z' => Some(ch as u8 - b'a' + 1),
        'A'..='Z' => Some(ch as u8 - b'A' + 1),
        '@' | ' ' => Some(0),
        '[' => Some(27),
        '\\' => Some(28),
        ']' => Some(29),
        '^' => Some(30),
        '_' => Some(31),
        '?' => Some(127),
        _ => None,
    }
}

fn function_key_to_bytes(number: u8) -> Option<Vec<u8>> {
    let bytes = match number {
        1 => b"\x1bOP".as_slice(),
        2 => b"\x1bOQ".as_slice(),
        3 => b"\x1bOR".as_slice(),
        4 => b"\x1bOS".as_slice(),
        5 => b"\x1b[15~".as_slice(),
        6 => b"\x1b[17~".as_slice(),
        7 => b"\x1b[18~".as_slice(),
        8 => b"\x1b[19~".as_slice(),
        9 => b"\x1b[20~".as_slice(),
        10 => b"\x1b[21~".as_slice(),
        11 => b"\x1b[23~".as_slice(),
        12 => b"\x1b[24~".as_slice(),
        _ => return None,
    };

    Some(bytes.to_vec())
}

struct RawMode;

impl RawMode {
    fn enter() -> Result<Self, Box<dyn Error>> {
        enable_raw_mode()?;
        Ok(Self)
    }
}

impl Drop for RawMode {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
    }
}

fn terminal_name() -> String {
    env::var("TERM").unwrap_or_else(|_| "xterm-256color".to_string())
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
