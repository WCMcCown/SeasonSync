# SeasonSync

SeasonSync is a Python automation tool that keeps wallpapers synchronized across multiple devices. The application automatically detects seasons, holidays, and special events, then updates a shared "Current" wallpaper directory that can be consumed by desktops, laptops, and digital displays on a network. It supports recurring events, dynamic date calculations (Easter, Thanksgiving, Memorial Day, etc.), and centralized background management.

## Features

- Automatic seasonal backgrounds
- Holiday scheduling
- Dynamic holiday calculations
  - Easter
  - Thanksgiving
  - Memorial Day
  - Father's Day
  - Kentucky Derby
- Centralized wallpaper management
- Multi-device synchronization

## Setup

1. Copy config.example.json to config.json
2. Edit paths
3. Run:

python seasonsync.py