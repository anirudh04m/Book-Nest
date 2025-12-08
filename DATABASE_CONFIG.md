# Database Configuration Guide

## Connection Methods

The application supports two authentication methods for SQL Server:

### Option 1: Windows Authentication (Trusted Connection)

Use this if you're on Windows and want to use your Windows credentials.

**`.env` file:**
```env
DB_SERVER=localhost
DB_NAME=BMS
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=yes
# Leave DB_USERNAME and DB_PASSWORD empty or don't include them
```

### Option 2: SQL Server Authentication (Username/Password)

Use this if you have a SQL Server login with username and password.

**`.env` file:**
```env
DB_SERVER=localhost
DB_NAME=BMS
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=no
DB_USERNAME=your_username
DB_PASSWORD=your_password
# Optional: specify port (defaults to 1433)
DB_PORT=1433
```

### Option 3: Remote SQL Server with Custom Port

**`.env` file:**
```env
DB_SERVER=your-server-name.database.windows.net
DB_NAME=BMS
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=no
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_PORT=1433
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_SERVER` | SQL Server hostname or IP | Yes | `localhost` |
| `DB_NAME` | Database name | Yes | `BMS` |
| `DB_DRIVER` | ODBC Driver name | Yes | `{ODBC Driver 17 for SQL Server}` |
| `DB_TRUSTED_CONNECTION` | Use Windows Auth | No | `yes` |
| `DB_USERNAME` | SQL Server username | Required if `DB_TRUSTED_CONNECTION=no` | - |
| `DB_PASSWORD` | SQL Server password | Required if `DB_TRUSTED_CONNECTION=no` | - |
| `DB_PORT` | SQL Server port | No | `1433` (default) |

## Example .env File

Create a `.env` file in the project root:

```env
# For Windows Authentication
DB_SERVER=localhost
DB_NAME=BMS
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=yes

# OR for SQL Server Authentication
# DB_SERVER=localhost
# DB_NAME=BMS
# DB_DRIVER={ODBC Driver 17 for SQL Server}
# DB_TRUSTED_CONNECTION=no
# DB_USERNAME=sa
# DB_PASSWORD=YourSecurePassword123
# DB_PORT=1433
```

## Notes

- The `.env` file should be in your `.gitignore` to keep credentials secure
- For production, use environment variables or a secure secrets manager
- Make sure the SQL Server allows the authentication method you're using

