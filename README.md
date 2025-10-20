# ECE326-Web-Search-Engine
A [web search engine](https://github.com/TszTungChau-Jo/ECE326-Web-Search-Engine) that resembles the Google search engine.

Author: Joshua Chau, Lynne Liu

## Search engine description
Frontend: You could open up a website and input anything in the search bar. The search bar will count how many times each word occur, and store in history. 
The website should show our logo and search engine name, two tables after search, and the cursor could turn into cat automatically within the web page. 

### Name
Meowgle ('Meow' + Google)

### Our logo
![Meowgle log](img/logo-png.png)
![Meowgle logo](img/design.png)

## LAB2: Frontend

### How to run
Open up the Terminal, enter the following:
```
python Lab2_F.py
```
Hit Enter. 

Open up your web browser, enter the following in the address:
```
http://localhost:8080
```

### Functionalities
1. Google Authorizer to allow users to sign in Google accounts and enter the web page with their histories (including top 10 searched).
   - New features:
     - Top 10 searched sentences are stored
     - Allow a signed-in user to open up the web page with the corresponding searching history on different devices
     - Allow the user to sign in using a Google account
3. An anonymous web page view is set up if the user doesn't want to sign in. This way, stored history will be cleaned once the anonymous user exits the web page. 

## LAB2: Backend
All scripts below are located in the `root/aws_acripts/` and were developed for ECE326 Lab 2 to automate EC2 lifecycle management, and some helper scripts for SSH setup or setup on the ec2 instance.

| File | Description |
|------|--------------|
| **`create_keypair.py`** | Creates a new AWS EC2 key pair using Boto3 and saves it as a `.pem` file for SSH access. |
| **`setup_security_group.py`** | Creates and configures a security group (`ece326-group3`) with inbound rules for SSH (22), HTTP (80), and ICMP (ping). |
| **`create_instance.py`** | Launches a new EC2 instance using a specified Ubuntu AMI, associates key pair and security group, and writes the instance ID and IP to `.env`. |
| **`list_instances.py`** | Lists all EC2 instances along with their state, type, and IP information for quick status checking. |
| **`start_instance.py`** | Starts a stopped EC2 instance defined in the `.env` file and refreshes the instance status. |
| **`stop_instance.py`** | Gracefully stops the running instance to avoid unnecessary compute charges while preserving data. |
| **`terminate_instance.py`** | Permanently terminates the EC2 instance and removes its EBS volume — irreversible. |
| **`reboot_instance.py`** | Performs a soft reboot of the instance (useful for applying configuration changes). |
| **`refresh_instance_info.py`** | Updates `.env` with the latest instance state and public IP after start/stop operations. |
| **`generate_ssh_helpers.py`** | Automatically generates reusable SSH and SCP helper commands for the active instance. |
| **`test_connection.py`** | Pings the EC2 instance and tests SSH connectivity using the stored key and IP to verify accessibility. |
| **`env_utils.py`** | Central utility for reading/writing environment variables (`.env`) and handling configuration consistency. |
| **`bootstrap.sh`** | Shell script to initialize the EC2 environment (install dependencies, update system packages, etc.) after instance creation. |

---

### Important Notes
- Currently, we only support managing one ec2 instance at a time.
- All scripts rely on environment variables managed through **`.env`** (e.g., `AWS_REGION`, `ECE326_INSTANCE_ID`, `KEY_PAIR_NAME`).

---

## LAB2: Benchmarking

### Resulting Files and Result
The resulting log files are stored inside `root/benchmark_results/`.
(I mistakenly deleted some of them, but the major ones are inside it.)

#### 1. Maximum Number of Connections
- **Max stable concurrency:** 28 (no failed requests at `n=10,000`)
- **Next level:** 30 (timed out after completing 9,978/10,000 requests)

#### 2. Maximum Sustained Throughput (at c=28)
- **Requests per second (mean):** 154.94 req/s  
- **Total requests:** 20,000  
- **Failed requests:** 0  

#### 3. Latency (at c=28)
- **Average (mean):** 180.712 ms  
- **99th percentile:** 1318 ms  

#### 4. Resource Utilization (measured via `dstat -cdnm 1`)
| Metric | Observation |
|--------|--------------|
| **CPU** | ~15–20% avg (peaks 25–44%), small `wai` (0–10%), occasional `stl` spikes |
| **Memory** | ~230–245 MB used, ~390–430 MB cache, ~100–140 MB free; no swap pressure |
| **Disk I/O** | Low (<1 MB/s), brief write bursts (16–60 MB/s) likely due to transient OS or logging activity |
| **Network** | ~60–80 KB/s received, ~700–950 KB/s sent — consistent with expected throughput (~4.4 KB × 155 req/s ≈ 680 KB/s) |

---

**Summary:**  
The Bottle web server running on a t3.micro EC2 instance handled up to **28 concurrent connections** stably, achieving **~155 requests per second** with **no failures** and maintaining low CPU/memory utilization throughout the test.  

---

### Benchmark Set Up: Creating A Tunnel
The client connects to the EC2 server using an **SSH tunnel** that forwards port 8080 from the remote instance to the local machine. The `.pem` file is included in the `root/`, and the current public IP of the ec2 instance is `34.207.252.88`.
To port forwarding to the ec2 instance: `ssh -i "ece326-group3-joshua-key.pem" -L 8080:localhost:8080 ubuntu@34.207.252.88`

**Command (run on local machine):**
```bash
ssh -i ~/.ssh/ece326-group3-joshua-key.pem \
    -o IdentitiesOnly=yes -o ExitOnForwardFailure=yes \
    -N -f -L 8080:localhost:8080 ubuntu@3.87.252.156
```

Explanation:

* -i ~/.ssh/ece326-group3-joshua-key.pem → specify private key

* -L 8080:localhost:8080 → forward local 8080 to remote 8080

* -N → no remote command (tunnel only)

* -f → run in background

* -o ExitOnForwardFailure=yes → exit if tunnel cannot be established

After setting up the tunnel, the web app hosted on the EC2 instance (port 8080) should be accessible from http://localhost:8080 on the local machine.

Benchmark Procedure

0. Remeber to install the benchmarking tools (`apache2-utils`, `dstat`, ...) before doing the test.

1. Launch the server on the EC2 instance

2. On the local machine, open the SSH tunnel (command above).

3. Run ApacheBench load tests from local terminal:

```bash
for c in 10 12 15 18 20 22 23 24 25 26 28 30; do
  echo "=== concurrency $c ==="
  ab -n 10000 -c $c http://localhost:8080/ | tee ab_c${c}_10k.log
done
```

4. Identify maximum concurrency before drops (c = 28), then run a sustained load test:

```bash
ab -n 20000 -c 28 http://localhost:8080/ | tee ab_max2.log
```

5. Monitor resource utilization on the EC2 instance (in another SSH session):

```bash
dstat -cdnm 1 | tee dstat.log
```

6. Stop the tunnel after testing:

```bash
pkill -f "ssh.*8080:localhost:8080"
```

## LAB1: How to run the front end
```
python -m http.server 8000
```

Then open http://localhost:8000/ locally

![Meowgle](Asset/Webpg.png)

### Files
img: Stores all images needed; Our logo, cursor, and web picture.

Important file for frontend: index.html, style.css, img, HelloWorld.py


## LAB1: Backend Design

### Overview
The backend extends on the given web crawler starter to index web pages and build an inverted index for efficient keyword search. The crawler visits URLs, extracts content, and maintains data structures that map words to the documents containing them.

### Main Data Structures

**1. Document Index (`_doc_index`)**
- **Type:** `dict[int, dict[str, str]]`
- **Purpose:** Stores metadata for each crawled document
- **Structure:** Maps document ID → {url, title, desc}
- **Example:**
  ```python
  {
    1: {
      "url": "http://google.com",
      "title": "Google",
      "desc": "Search the world's information..."
    }
  }
  ```

**2. Inverted Index (`_inverted_index`)**
- **Type:** `dict[int, set[int]]`
- **Purpose:** Maps word IDs to the set of documents containing that word
- **Structure:** word_id → set(doc_ids)
- **Example:**
  ```python
  {
    1: {1, 2, 3},  # "google" appears in docs 1, 2, 3
    2: {1, 4}      # "search" appears in docs 1, 4
  }
  ```

**3. Lexicon (`_word_id_cache`)**
- **Type:** `dict[str, int]`
- **Purpose:** Maps each unique word to a unique word ID
- **Structure:** word → word_id
- **Example:**
  ```python
  {
    "google": 1,
    "search": 2,
    "engine": 3
  }
  ```

**4. Document ID Cache (`_doc_id_cache`)**
- **Type:** `dict[str, int]`
- **Purpose:** Prevents duplicate crawling by tracking all seen URLs
- **Structure:** url → doc_id

### Required Functionality 1: get_inverted_index()

**Purpose:** Returns the inverted index with word IDs and document IDs

**Return Type:** `dict[int, set[int]]`

**Behavior:**
- Returns a shallow copy of the internal inverted index
- Prevents external modifications from corrupting internal state
- Maps word_id → set of doc_ids where the word appears

**Example Usage:**
```python
bot = crawler(None, "urls.txt")
bot.crawl(depth=0)
index = bot.get_inverted_index()
# Returns: {1: {1, 2}, 2: {1, 3}, ...}
```

### Required Functionality 2: get_resolved_inverted_index()

**Purpose:** Returns the inverted index with actual words and URLs instead of IDs

**Return Type:** `dict[str, set[str]]`

**Behavior:**
- Translates word IDs to actual words using the lexicon
- Translates document IDs to URLs using the document index
- Returns a human-readable version of the inverted index
- Only includes words and documents that were successfully indexed

**Example Usage:**
```python
bot = crawler(None, "urls.txt")
bot.crawl(depth=0)
resolved = bot.get_resolved_inverted_index()
# Returns: {
#   "google": {"http://google.com", "http://google.ca"},
#   "search": {"http://google.com", "http://bing.com"}
# }
```

### Running the Backend

**Crawl URLs:**
```bash
python crawler.py
```

**Run Unit Tests:**
```bash
python -m unittest -v test_crawler_lab1.py
```

**Expected Output:**
```
test_get_inverted_index_returns_dict ... ok
test_inverted_index_structure ... ok
test_get_resolved_inverted_index_returns_dict ... ok
test_resolved_index_structure ... ok
test_doc_index_has_required_fields ... ok
test_descriptions_exist ... ok
test_ignored_words_filtered ... ok

Ran 7 tests in 0.5s
OK
```

### Files

**Important files for backend:**
- `crawler.py` - Main crawler implementation with indexing logic
- `test_crawler_lab1.py` - Unit tests verifying crawler functionality
- `urls.txt` - Seed URLs for the crawler to start from
- `requirements.txt` - Python dependencies (BeautifulSoup, etc.)
