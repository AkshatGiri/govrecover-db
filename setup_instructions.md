## Setting up the linode server

1. Go to linode.com and sign in
2. Create a new linode ( I've used 4gb ram 2 cores and 80gb storage and it's been fine )
3. Select the postgres template from the marketplace

## Configuring Postgres

The postgres db is running on the server but we need to make a few changes to make it available for remote connections.

### First let's change the password for the database

Let's enter the postgres shell

```bash
sudo -i -u postgres
```

Within the postgres shell enter psql shell by entering.

```bash
psql
```

Next execute the following command to change the password.

```sql
ALTER USER postgres PASSWORD 'mynewpassword';
```

Now we have a user and password for the database that we can use to connect to it.

```
user - postgres
password - mynewpassword
```

### Opening up the database for remote connections

Configure PostgreSQL to Listen on All IP Addresses Open the configuration file (postgresql.conf) located in:

```bash
sudo vim /etc/postgresql/13/main/postgresql.conf
```

Change the listen_addresses line to:

```
listen_addresses = '*'
```

👆 Note: The line above is usually commented out, so make sure to uncomment it.

Modify pg_hba.conf for Remote Access Open pg_hba.conf:

```bash
sudo vim /etc/postgresql/13/main/pg_hba.conf
```

To open Ipv4 connection and allow remote connections add the following line to:

```
host    all             all             0.0.0.0/0               md5
```

NOTE: there might be other ipv4 lines in the file, make sure comment it out or remove it. ( I haven't tested what happens when both lines are present, it might be okay if we just add the line to the end.)

### Adjust the Firewall with ufw

If using ufw, allow traffic on the PostgreSQL port (5432):

```bash
sudo ufw allow 5432/tcp
```

Check the status

```bash
sudo ufw status
```

### Restart the postgres service

Apply the configuration changes by restarting PostgreSQL:

```bash
sudo systemctl restart postgresql
```

Perfect, now that postgres is ready to accept remote connections. You can connect to it using it's public ip ( can be found on the linode dashboard ). You can use the pgadmin tool or the command line psql.

```
USER = postgres
PASSWORD = mynewpassword
DB_HOST = { public server ip address }
DB_PORT=5432
```

## TODO: Setup the script
