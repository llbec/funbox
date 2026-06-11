use std::{
    env,
    error::Error,
    fmt, fs,
    io::{self, Write},
    path::{Path, PathBuf},
};

use arboard::Clipboard;
use serde::Deserialize;

const DEFAULT_CONFIG_FILE: &str = "clips.json";

#[derive(Debug, Clone)]
struct ClipItem {
    description: String,
    text: String,
}

#[derive(Debug, Deserialize)]
struct ClipItemConfig {
    description: String,
    text: String,
}

#[derive(Debug)]
struct AppError(String);

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl Error for AppError {}

fn main() {
    if let Err(err) = run() {
        eprintln!("error: {err}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn Error>> {
    let config_path = parse_config_path()?;
    let items = read_clip_items(&config_path)?;
    let selected = select_clip_item(&items)?;

    copy_to_clipboard(&selected.text)?;
    println!("Copied: {}", selected.description);

    Ok(())
}

fn parse_config_path() -> Result<PathBuf, Box<dyn Error>> {
    let mut args = env::args().skip(1);
    let first = match args.next() {
        Some(value) => value,
        None => return Ok(default_config_path()),
    };

    if first == "-h" || first == "--help" {
        print_help();
        std::process::exit(0);
    }

    if args.next().is_some() {
        return Err(Box::new(AppError(
            "too many arguments; pass at most one config file path".to_string(),
        )));
    }

    Ok(PathBuf::from(first))
}

fn print_help() {
    println!(
        "quick_clipboard\n\nUsage:\n  quick_clipboard [config-file]\n\nIf config-file is omitted, quick_clipboard reads clips.json next to the executable."
    );
}

fn default_config_path() -> PathBuf {
    env::current_exe()
        .ok()
        .and_then(|path| path.parent().map(|parent| parent.join(DEFAULT_CONFIG_FILE)))
        .unwrap_or_else(|| PathBuf::from(DEFAULT_CONFIG_FILE))
}

fn read_clip_items(path: &Path) -> Result<Vec<ClipItem>, Box<dyn Error>> {
    let content = fs::read_to_string(path).map_err(|err| {
        AppError(format!(
            "failed to open config file '{}': {err}",
            path.display()
        ))
    })?;
    let configs: Vec<ClipItemConfig> = serde_json::from_str(&content).map_err(|err| {
        AppError(format!(
            "failed to parse JSON config file '{}': {err}",
            path.display()
        ))
    })?;

    let items = configs
        .into_iter()
        .enumerate()
        .map(|(index, config)| ClipItem::try_from_config(index + 1, config))
        .collect::<Result<Vec<_>, _>>()?;

    if items.is_empty() {
        return Err(Box::new(AppError(format!(
            "no clip entries found in '{}'",
            path.display()
        ))));
    }

    Ok(items)
}

impl ClipItem {
    fn try_from_config(index: usize, config: ClipItemConfig) -> Result<Self, Box<dyn Error>> {
        Ok(Self {
            description: required_field(index, "description", config.description)?,
            text: required_field(index, "text", config.text)?,
        })
    }
}

fn required_field(index: usize, field_name: &str, value: String) -> Result<String, Box<dyn Error>> {
    let value = value.trim();
    if value.is_empty() {
        return Err(Box::new(AppError(format!(
            "clip #{index}: {field_name} cannot be empty"
        ))));
    }

    Ok(value.to_string())
}

fn select_clip_item(items: &[ClipItem]) -> Result<&ClipItem, Box<dyn Error>> {
    println!("Available clips:");
    println!("{:<4} {}", "No.", "Description");

    for (index, item) in items.iter().enumerate() {
        println!("{:<4} {}", index + 1, item.description);
    }

    loop {
        print!("Select clip number: ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        match input.trim().parse::<usize>() {
            Ok(number) if (1..=items.len()).contains(&number) => {
                return Ok(&items[number - 1]);
            }
            _ => println!("Please enter a number between 1 and {}.", items.len()),
        }
    }
}

fn copy_to_clipboard(text: &str) -> Result<(), Box<dyn Error>> {
    let mut clipboard = Clipboard::new()
        .map_err(|err| AppError(format!("failed to access system clipboard: {err}")))?;
    clipboard
        .set_text(text.to_string())
        .map_err(|err| AppError(format!("failed to copy text to system clipboard: {err}")))?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_empty_description() {
        let config = ClipItemConfig {
            description: " ".to_string(),
            text: "value".to_string(),
        };

        assert!(ClipItem::try_from_config(1, config).is_err());
    }

    #[test]
    fn trims_config_values() {
        let config = ClipItemConfig {
            description: "  token  ".to_string(),
            text: "  abc123  ".to_string(),
        };

        let item = ClipItem::try_from_config(1, config).unwrap();

        assert_eq!(item.description, "token");
        assert_eq!(item.text, "abc123");
    }
}
