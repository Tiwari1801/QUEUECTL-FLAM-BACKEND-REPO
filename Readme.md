# 🚀 QueueCTL --- Background Job Queue System (CLI + FastAPI) {#queuectl-background-job-queue-system-cli-fastapi}

QueueCTL is a **CLI-based background job queue system** built in
**Python**.  
It manages background jobs with multiple workers, automatic retries
using exponential backoff, and a Dead Letter Queue (DLQ) for permanently
failed jobs.

## 📸 Project Overview {#project-overview}

> 🖼️ *Paste your architecture or flow diagram here*  
> Example:  
> Architecture Diagram

## 🧠 Features {#features}

✅ Enqueue and manage background jobs  
✅ Run multiple workers in parallel  
✅ Automatic retries with exponential backoff  
✅ Persistent storage using SQLite  
✅ Dead Letter Queue (DLQ) support  
✅ Graceful worker shutdown  
✅ Configurable retry and backoff parameters  
✅ Optional FastAPI monitoring server

## ⚙️ Tech Stack {#tech-stack}

| Component     | Technology  |
|---------------|-------------|
| Language      | Python 3.12 |
| CLI Framework | Typer       |
| Database      | SQLite      |
| API           | FastAPI     |
| Web Server    | Uvicorn     |

## 🧩 Project Structure {#project-structure}

    queuectl/
    ├── queuectl/
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── worker.py
    │   ├── models.py
    │   ├── db.py
    │   ├── config.py
    │   ├── utils.py
    │   ├── api.py
    ├── tests/
    │   ├── smoke_test.bat
    ├── queuectl.py
    └── README.md

> 🖼️ *Paste a screenshot of your folder structure here*  
> Folder structure

## ⚡ Setup Instructions {#setup-instructions}

### 1️⃣ Clone or copy this project {#clone-or-copy-this-project}

    git clone https://github.com/<your-username>/QueueCTL.git
    cd QueueCTL

### 2️⃣ Create and activate a virtual environment {#create-and-activate-a-virtual-environment}

    python -m venv .venv
    .\.venv\Scripts\activate

### 3️⃣ Install dependencies {#install-dependencies}

    pip install typer fastapi uvicorn sqlalchemy python-dotenv

![](media/image1.png){width="6.5in" height="1.6534722222222222in"}

## 🪮 Initialize the Database {#initialize-the-database}

    python queuectl.py status

✅ Expected output:

## 🚀 CLI Commands {#cli-commands}

### 🟢 Enqueue a Job {#enqueue-a-job}

    python queuectl.py enqueue "{\"id\":\"job1\",\"command\":\"echo Hello World\"}"
    python queuectl.py enqueue "{\"id\":\"job2\",\"command\":\"bash -c 'exit 1'\"}"

✅ Output:

![](media/image3.png){width="6.5in" height="1.6291666666666667in"}

### 🧵 Start Worker(s) {#start-workers}

    python queuectl.py worker start --count 2

✅ Output:

![](media/image4.png){width="6.5in" height="2.1131944444444444in"}

### 📊 Check Queue Status {#check-queue-status}

    python queuectl.py status

✅ Output:

> ![](media/image5.png){width="6.319444444444445in"
> height="2.198611111111111in"}

### 🧾 List Jobs {#list-jobs}

    python queuectl.py list 

✅ Output:

![](media/image6.png){width="6.5in" height="3.4506944444444443in"}

### 💀 Dead Letter Queue (DLQ) {#dead-letter-queue-dlq}

    python queuectl.py dlq-list

✅ Output:

![](media/image7.png){width="6.5in" height="2.209722222222222in"}

### 🔁 Retry DLQ Job {#retry-dlq-job}

    python queuectl.py dlq-retry job2

![](media/image8.png){width="6.5in" height="2.3020833333333335in"}

### ⚙️ Configuration {#configuration}

Change retry or backoff parameters:

    python queuectl.py config-set max_retries 5
    python queuectl.py config-set backoff_base 3

![](media/image9.png){width="6.5in" height="1.7722222222222221in"}

### 🧪 Run Full Smoke Test (Windows) {#run-full-smoke-test-windows}

    tests\smoke_test.bat

![](media/image10.png){width="6.5in" height="3.388888888888889in"}

![](media/image11.png){width="6.5in" height="3.4131944444444446in"}

## 🌐 Run the FastAPI Monitoring Server {#run-the-fastapi-monitoring-server}

Start the API server:

    uvicorn queuectl.api:app --reload --port 8000

Then open in your browser: - http://127.0.0.1:8000/jobs  
- http://127.0.0.1:8000/jobs/job1

![](media/image12.png){width="6.5in" height="1.7756944444444445in"}

![](media/image13.png){width="6.5in" height="4.45625in"}

![](media/image14.png){width="6.5in" height="3.464583333333333in"}

## 🧹 Reset / Clear the Queue {#reset-clear-the-queue}

You can delete all jobs manually:

*python -m sqlite3 %HOMEPATH%\\queuectl.db \"DELETE FROM jobs;\"*

![](media/image15.png){width="6.5in" height="1.0895833333333333in"}

## 🧠 How It Works {#how-it-works}

1.  Jobs are added to the SQLite database in `pending` state.
2.  Worker threads pick the oldest pending job.
3.  Each job executes its command (`subprocess.run`).
4.  On failure → retries with exponential backoff
    (`delay = base ** attempts`).
5.  After exceeding `max_retries` → job moves to `dead` state (DLQ).
6.  Jobs and states persist across restarts.

> 🖼️ *Paste diagram of job lifecycle here*  
> Flow Diagram

## ✅ Verified Test Scenarios {#verified-test-scenarios}

| Scenario                       | Status |
|--------------------------------|--------|
| Successful job execution       | ✅     |
| Failed job retry               | ✅     |
| Dead Letter Queue handling     | ✅     |
| DLQ retry mechanism            | ✅     |
| Persistent data across restart | ✅     |
| Config updates                 | ✅     |
| Graceful shutdown              | ✅     |

## 🧱 Possible Enhancements {#possible-enhancements}

- Add job priority queue
- Scheduled/delayed jobs (`run_at`)
- Job timeout handling
- Job result logging
- Simple web dashboard with metrics

> 🖼️ *Paste optional roadmap image here*  
> Roadmap

## 🧩 Contributing {#contributing}

Pull requests are welcome!  
If you'd like to enhance the queue, fork the repo and submit a PR.

## 👨‍💻 Author {#author}

**Aditya Tiwari**  
B.Tech CSE --- PES University  
*Backend Developer Internship Assignment --- QueueCTL*

## 🧮 Git Commands to Push This Project {#git-commands-to-push-this-project}

> 💡 *Use these if your GitHub repo hasn't been created yet.*

### 1️⃣ Initialize git and commit your code {#initialize-git-and-commit-your-code}

    git init
    git add .
    git commit -m "Initial commit - QueueCTL project"

### 2️⃣ Create a new repo on GitHub {#create-a-new-repo-on-github}

Go to 🔗 <https://github.com/new>  
- Repository name: **QueueCTL**  
- Visibility: **Public**  
- Do **not** add README (you already have one)

### 3️⃣ Link local repo to GitHub {#link-local-repo-to-github}

    git remote add origin https://github.com/<your-username>/QueueCTL.git

### 4️⃣ Push to GitHub {#push-to-github}

    git branch -M main
    git push -u origin main

> 🖼️ *Paste screenshot of successful push to GitHub*  
> Git push

## 🎥 Demo Video {#demo-video}

> 🎬 *Record a short demo showing enqueue, workers, retries, and DLQ.*

Upload to Google Drive or YouTube, then paste the link below:

📎 **Demo Link:** \[Add your video demo link here\]

> 💬 *QueueCTL was developed as part of a backend developer internship
> assignment to demonstrate command-line tool development, concurrency,
> persistence, and retry mechanisms.*
