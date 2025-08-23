# ♔ Professional Chess Game with Stockfish ♕

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange?logo=python&logoColor=white)
![Stockfish](https://img.shields.io/badge/Engine-Stockfish-red?logo=chess.com&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

<div align="center">

**A feature-rich, professional chess game with advanced AI integration**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

This is a **professional-grade chess application** built with **Python** and **Tkinter**, featuring full integration with the powerful **Stockfish chess engine**. The game provides an intuitive interface for both casual players and chess enthusiasts, offering multiple game modes, real-time analysis, and comprehensive chess features.

Whether you're looking to practice against a world-class AI, analyze your games, or simply enjoy a game with a friend, this application has everything you need.

---

## ✨ Features

### 🤖 **AI Integration**
- **Stockfish engine** integration with adjustable difficulty
- Skill levels from **0 to 20** (Elo 1320–3190)
- Real-time position evaluation
- Multiple thinking time settings

### 🎮 **Game Modes**
- **Player vs Player** (local multiplayer)
- **Player vs AI** (with customizable difficulty)
- **Analysis mode** for position review

### 📊 **Advanced Features**
- **Real-time evaluation** with numerical scores
- **Move history navigation** (forward/backward through games)
- **Interactive board** with legal move highlights
- **Last move highlighting** for better visualization
- **Undo/Redo functionality**

### 📝 **Game Management**
- **PGN format support** (save/load games)
- **Copy PGN to clipboard** for easy sharing
- **Game statistics** and move tracking
- **Position setup** from FEN notation

### 🎨 **Customization**
- **Custom board themes** and piece sets
- **Resizable interface** for different screen sizes
- **Board flip** functionality
- **Configurable highlights** and animations

### ⌨️ **User Experience**
- **Comprehensive keyboard shortcuts**
- **Intuitive drag-and-drop** piece movement
- **Built-in chess rules guide**
- **Context menus** for quick actions

---

## 🚀 Installation

### Prerequisites
- **Python 3.10+** installed on your system
- **Stockfish engine** (will be guided through installation)

### Step 1: Clone the Repository
```bash
git clone https://github.com/LechehebDjaafar/professional-chess-game.git
cd professional-chess-game
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download Stockfish Engine
1. Visit the [official Stockfish website](https://stockfishchess.org/download/)
2. Download the appropriate version for your operating system
3. Extract the executable and place it in the project folder as `stockfish.exe` (Windows) or `stockfish` (Linux/macOS)

**Alternative:** The application will guide you to specify the Stockfish path on first run.

### Step 4: Run the Game
```bash
python GameChess.py
```

---

## 📦 Dependencies

The application requires the following Python packages:

- **python-chess** - Chess library for move generation, validation, and PGN handling
- **Pillow (PIL)** - Image processing for custom piece sets and board themes
- **Tkinter** - GUI framework (included with Python standard library)

**Additional standard libraries used:**
- **threading** - For non-blocking AI calculations
- **asyncio** - Asynchronous operations with chess engine
- **io** - File and stream operations
- **os** - Operating system interface
- **time** - Time-related functions
- **random** - Random number generation

All dependencies are listed in `requirements.txt` for easy installation.

---

## 🎮 Usage

### Starting a New Game
1. Launch the application
2. Choose your preferred game mode:
   - **vs Player**: Local multiplayer game
   - **vs Stockfish**: Play against the AI
3. Configure difficulty settings (for AI games)
4. Start playing!

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New Game |
| `Ctrl + Z` | Undo Move |
| `Ctrl + Y` | Redo Move |
| `Ctrl + O` | Open PGN File |
| `Ctrl + S` | Save Game as PGN |
| `Ctrl + C` | Copy PGN to Clipboard |
| `Ctrl + F` | Flip Board |
| `Space` | Pause/Resume Game |
| `←` / `→` | Navigate Move History |
| `Home` / `End` | Jump to Start/End of Game |
| `F1` | Show Chess Rules Help |
| `Esc` | Return to Main Menu |

### Game Controls
- **Left-click**: Select piece or make move
- **Right-click**: Show context menu
- **Drag & Drop**: Move pieces intuitively
- **Double-click**: Quick move (if only one legal move available)

---

## 🖼️ Screenshots

*Add your screenshots here to showcase the application interface*

```
[Main Menu]     [Game Board]     [Settings Panel]
```

---

## ⚙️ Configuration

The application stores configuration in a local settings file, including:

- Stockfish engine path
- Preferred difficulty levels
- Board themes and colors
- Keyboard shortcut preferences
- Window size and position

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Bug Reports
- Use the [Issues](https://github.com/LechehebDjaafar/professional-chess-game/issues) page
- Include detailed steps to reproduce
- Specify your operating system and Python version

### Feature Requests
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Consider contributing the implementation!

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

---

## 📋 Roadmap

### Upcoming Features
- [ ] **Online multiplayer** support
- [ ] **Chess.com/Lichess** integration
- [ ] **Opening book** database
- [ ] **Puzzle solving** mode
- [ ] **Tournament mode** for multiple games
- [ ] **Engine vs Engine** matches
- [ ] **Mobile app** version

### Technical Improvements
- [ ] **Database** integration for game storage
- [ ] **Advanced graphics** with piece animations
- [ ] **Sound effects** and audio feedback
- [ ] **Accessibility** features
- [ ] **Multi-language** support

---

## 🐛 Known Issues

- Stockfish path configuration may need manual setup on some systems
- Large PGN files might take time to load
- Windows Defender may flag the Stockfish executable (false positive)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Feel free to use, modify, and distribute this software.
```

---

## 👨‍💻 Author

**DJaafar Lachehab** (لشهب جعفر)  
🎓 Computer Engineer | ♟️ Chess Enthusiast | ⚙️ Software Developer

🇩🇿 **Made with ❤️ in Algeria**

---

## 🙏 Acknowledgments

- **Stockfish Team** - For the incredible chess engine
- **Python-Chess Library** - For comprehensive chess functionality
- **Chess.com** - For inspiration and chess piece designs
- **The Chess Community** - For feedback and testing

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/) folder
2. Search [existing issues](https://github.com/LechehebDjaafar/professional-chess-game/issues)
3. Create a new issue if needed
4. Join our community discussions

---

<div align="center">

**⭐ If you enjoy this project, please give it a star! ⭐**

[Report Bug](https://github.com/LechehebDjaafar/professional-chess-game/issues) • [Request Feature](https://github.com/LechehebDjaafar/professional-chess-game/issues) • [Contribute](CONTRIBUTING.md)

</div>