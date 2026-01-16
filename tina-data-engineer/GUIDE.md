# Getting Started Guide - Data Engineering Environment

## Step 1: Start Docker Desktop

1. Look for the **Docker** icon on your Mac (it looks like a whale with containers)
2. Click on it to open Docker Desktop
3. Wait until you see "Docker Desktop is running" in the menu bar
4. This usually takes 30-60 seconds

## Step 2: Start Your Development Environment

1. Open **Terminal** (you can find it in Applications > Utilities)
2. Type this command and press Enter:
   ```bash
   cd ~/zz/Documents/tina-data-engineer
   ```
3. Then type this command and press Enter:
   ```bash
   docker-compose up -d
   ```
4. Wait for it to finish (you'll see "Started" messages)

## Step 3: Check Everything is Running

Type this command in Terminal:
```bash
docker ps
```

You should see 3 containers running:
- **tina-devtools** - Your workspace
- **tina-mysql** - MySQL database
- **tina-postgres** - PostgreSQL database

## Step 4: Access Jupyter Notebook

1. Open your web browser (Safari, Chrome, etc.)
2. Go to this address:
   ```
   http://localhost:8888
   ```
3. You should see the Jupyter Notebook interface
4. No password needed - it will open directly

## Database Connection Information

### MySQL Database
- **Host**: localhost
- **Port**: 3306
- **Username**: devuser
- **Password**: devpassword
- **Database Name**: devdb

### PostgreSQL Database
- **Host**: localhost
- **Port**: 5432
- **Username**: devuser
- **Password**: devpassword
- **Database Name**: devdb

## How to Stop Everything

When you're done working, type this in Terminal:
```bash
cd ~/zz/Documents/tina-data-engineer
docker-compose down
```

## Your Work Files

All your notebooks and files are saved in:
```
~/zz/Documents/tina-data-engineer/workspace
```

You can access this folder from Finder too!

## Troubleshooting

### Problem: "Cannot connect to Docker"
**Solution**: Make sure Docker Desktop is running (check the whale icon in your menu bar)

### Problem: "Port already in use"
**Solution**: Stop the containers first with `docker-compose down`, then start again

### Problem: Can't access http://localhost:8888
**Solution**: 
1. Check containers are running: `docker ps`
2. If not running, start them: `docker-compose up -d`
3. Wait 10 seconds and try again

## Need Help?

If something doesn't work:
1. Stop everything: `docker-compose down`
2. Start Docker Desktop again
3. Wait for it to be ready
4. Run `docker-compose up -d` again

## Adding New Python Packages

To add more Python libraries in the future:

1. Edit the file: `~/zz/Documents/tina-data-engineer/requirements.txt`
2. Add your new package name (one per line)
3. Rebuild and restart:
   ```bash
   cd ~/zz/Documents/tina-data-engineer
   docker-compose down
   docker-compose build devtools
   docker-compose up -d
   ```

**Quick Install (Temporary)**: For testing, you can install directly:
```bash
docker exec -it tina-devtools pip install <package-name>
```
Note: This will be lost when container is rebuilt.

---

**Quick Reference Card**

| What | Command |
|------|---------|
| Start everything | `docker-compose up -d` |
| Stop everything | `docker-compose down` |
| Check status | `docker ps` |
| Jupyter URL | http://localhost:8888 |
