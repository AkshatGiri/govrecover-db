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

### Creat a new database

```sql
CREATE DATABASE govrecover;
```

## Setup the script

### Installing the dependencies

The server probably doesn't come with git installed so let's do that.

```bash
sudo apt install git
```

Clone this repo

```bash
git clone https://github.com/AkshatGiri/govrecover-db.git
```

There should be python3 installed on the server but we might need to install pip3.

```bash
sudo apt install python3-pip
```

Change directory to the repo

```bash
cd govrecover-db
```

Install the dependencies

```bash
pip3 install -r requirements.txt
```

### Add a .env file

```
DB_NAME=govrecover
DB_USER=postgres
DB_PASSWORD=mynewpassword
DB_HOST=localhost
DB_PORT=5432
```

## Run the script

```bash
python3 main.py
```

Now let it do it's thing. Should take about 15 minutes to finish.

## Setup the automation

The list is realeased every thursday morning. So we want the python script to fire off around 8am every thursday.

Make the script executable

```bash
chmod +x main.py
```

We're going to use crontab to make the cronjob

```bash
crontab -e
```

This will open a a file in vim or nano based on what you selected.

Add the following line to the file.

```
0 15 * * 4 /root/govrecover-db/main.py >> /root/govrecover-db/logs.log 2>&1
```

Explanation of the line above

```
0 - minute
15 - hour ( 3pm which is 8am PST, there's some weirdness around the daylight savings, so might have to switch to 16 when daylight saving is on or off idk. )
* - day of the month
* - month
4 - day of the week ( 0 is sunday, 4 is thursday )

/root/govrecover-db/main.py - the script to run

>> /root/govrecover-db/logs.log - The file to save logs to.

2>&1 - Redirects the stderr to stdout so that we can save it to the logs file.
```
