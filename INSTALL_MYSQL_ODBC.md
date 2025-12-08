# Installing MySQL ODBC Driver on macOS

## Current Status

The code has been updated to use MySQL instead of SQL Server.

## Install MySQL ODBC Driver

### Option 1: Using Homebrew (Recommended)

```bash
brew install mysql-connector-odbc
```

### Option 2: Download from MySQL Website

1. Visit: https://dev.mysql.com/downloads/connector/odbc/
2. Download the macOS installer
3. Install the package

### Option 3: Using pip (Alternative - uses PyMySQL instead)

If ODBC doesn't work, you can switch to using `pymysql` or `mysql-connector-python`:

```bash
pip install pymysql
# OR
pip install mysql-connector-python
```

Then update the code to use these libraries instead of pyodbc.

## Verify Installation

Check installed drivers:
```bash
odbcinst -q -d
```

You should see something like:
```
[MySQL ODBC 8.0 Unicode Driver]
[MySQL ODBC 8.0 ANSI Driver]
```

## Configuration

Update your `.env` file:

```env
DB_SERVER=localhost
DB_NAME=BMS
DB_DRIVER={MySQL ODBC 8.0 Unicode Driver}
DB_USERNAME=admin
DB_PASSWORD=sql56789
DB_PORT=3306
```

## Common MySQL ODBC Driver Names

- `{MySQL ODBC 8.0 Unicode Driver}` (recommended)
- `{MySQL ODBC 8.0 ANSI Driver}`
- `{MySQL ODBC 5.3 Unicode Driver}`
- `{MySQL ODBC 5.3 ANSI Driver}`

The code will automatically try these if the configured driver is not found.

