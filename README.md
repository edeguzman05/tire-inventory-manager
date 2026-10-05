# Tire Inventory System

Local tire inventory management application for Garcia Wheels & Tires.

## Features
- New and used tire inventory
- Barcode support
- Tire-size search
- Sales tracking
- Store-specific inventory
- Database backups

## Run From Source

python gui.py

## Run Tests

python -m unittest unitTests.testInventory

## Installation

### Normal Installation

1. Download `TireInventorySetup.exe`.
2. Double-click the installer.
3. Follow the installation prompts.
4. A **Tire Inventory** shortcut will be created on the desktop.
5. Launch Tire Inventory.
6. On first launch, enter the name of the store/location.
7. Begin adding inventory.

Python is not required to run the installed application.

### First-Time Setup

Each computer maintains its own independent inventory.

The application stores its data locally in:

`%LOCALAPPDATA%\TireInventory`

This folder contains:

- `inventory.db` - inventory and sales database
- `settings.json` - store/location settings

Do not manually delete these files once the store begins using the
application with real inventory.

### Multiple Store Locations

Install the same `TireInventorySetup.exe` on each store computer.

Each computer will automatically create its own independent database.
Inventory entered at one store will not affect the other store.

### Creating Backups

1. Open Tire Inventory.
2. Click **Backup Inventory**.
3. Select a backup location.
4. The application creates a timestamped SQLite backup.

Example:

`Garcia_Wheels_Tires_inventory_backup_2026-10-05_18-30-00.db`

Backups should preferably be stored somewhere other than the shop
computer, such as a USB drive, external drive, or secure cloud-backed
folder.

### Updating the Application

Installing a newer version of Tire Inventory does not normally replace
the inventory database because application data is stored separately
under `%LOCALAPPDATA%\TireInventory`.

A database backup should still be created before installing an update.

### Windows Security Warning

Because the application is independently distributed and is not
currently digitally signed, Windows SmartScreen may display a warning.

Only install copies obtained directly from the project's trusted
distribution source.