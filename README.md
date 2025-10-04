# Dinero
**Dinero**, 'money' in Spanish, is a cryptocurrency developed entirely in Python and utilizes PostgreSQL for it's blockchain. It's a fork of [Denaro](https://github.com/denaro-coin/denaro). Dinero is also partially compatible with Denaro. That means you can use some of the tools made for Denaro on the Dinero blockchain.

* **Features**: 
  * Maximum supply of 30,062,005 coins.
  * Allows for transactions with up to 6 decimal places.
  * Blocks are generated approximately every ~3 minutes, with a limit of 2MB per block.
  * Given an average transaction size of 250 bytes (comprising of 5 inputs and 2 outputs), a single block can accommodate approximately ~8300 transactions, which translates to about ~40 transactions per second.

## Projects for the Denaro coin
* [Denaro Wallet Client GUI](https://github.com/The-Sycorax/DenaroWalletClient-GUI)
* [Denaro Wallet Client CLI](https://github.com/The-Sycorax/DenaroWalletClient)
* [Denaro CUDA Pool miner](https://github.com/1460293896/denaro-cuda-miner)
* [DenaroCudaMiner (Solo)](https://github.com/witer33/denarocudaminer)
* [Denaro WASM Miner](https://github.com/geiccobs/denaro-wasm-miner)
* [Denaro CPU Pool Miner](https://github.com/geiccobs/denaro-pool-miner)
* [Denaro CPU Solo Miner](https://github.com/geiccobs/denaro-solo-miner)
* [DVM (Denaro Virtual Machine)](https://github.com/denaro-coin/dvm)
* [Denaro Vanity Generator](https://github.com/The-Sycorax/Denaro-Vanity-Generator)
* [Denaro-Vanity-Gen](https://github.com/Avecci-Claussen/Denaro-Vanity-Gen)

Some of these projects may be not cmpatible with Dinero.

## Installation
**Automated configuration and deployment of a Dinero node are facilitated by the `setup.sh` script. It handles system package updates, manages environment variables, configures the PostgreSQL database, sets up a Python virtual environment, installs the required Python dependencies, and initiates the Dinero node. This script ensures that all prerequisites for operating a Denaro node are met and properly configured accoring to the user's preference.**
 
- The setup script accepts three optional arguments to adjust its behavior during installation:

  - `--skip-prompts`: Executes the setup script in an automated manner without requiring user input, bypassing all interactive prompts.
  
  - `--setup-db`: Limits the setup script's actions to only configure the PostgreSQL database, excluding the execution of other operations such as virtual environment setup and dependency installation.

  - `--skip-package-install`: Skips APT package installation. This can be used for Linux distributions that do not utilize APT as a package manager. However, it is important that the required system packages are installed prior to running the setup script (For more details refer to: *Installation for Non-Debian Based Systems*).

**Execute the commands below to initiate the installation:**

  ```bash
  # Clone the Dinero repository to your local machine.
  git clone https://github.com/Gamer000gaming/dinero-coin.git
  
  # Change directory to the cloned repository.
  cd denaro
  
  # Make the setup script executable.
  chmod +x setup.sh
  
  # Execute the setup script with optional arguments if needed.
  ./setup.sh [--skip-prompts] [--setup-db] [--skip-package-install]
  ```

<details>
<summary>Installation for Non-Debian Based Systems:</summary>

<dl><dd>
<dl><dd>

 The setup script is designed for Linux distributions that utilize `apt` as their package manager (e.g. Debian/Ubuntu). If system package installation is unsuccessful, it may be due to the absence of apt on your system. In which case, the required system packages must be installed manually. Below you will find a list of the required system packages.

<details>
<summary>Required Packages:</summary>
<dl><dd>

*Note: It is nessessary to ensure that the package names specified are adjusted to correspond with those recognized by your package manager.*

- `gcc`
- `libgmp-dev`
- `libpq-dev`
- `postgresql`
- `python3`
- `python3-venv` (If using a python virtual environment)
- `sudo`
  
</dd></dl>
</details>

Once the required packages have been installed, the `--skip-package-install` argument can be used with the setup script to bypass operations which require 'apt', thus mitigating any unsucessful execution relating to package installation.

</dd></dl>
</dd></dl>
</details>

## Running a Dinero Node

A Dinero node can be started manually if you have already executed the `setup.sh` script and chose not to start the node immediately, or if you need to start the node in a new terminal session. 

***Note:** Users who have used the setup script with the `--setup-db` argument or have performed a manual installation, should create a Python virtual environment (Optional) and ensure that the required Python packages are installed prior to starting a node.*

Execute the commands below to manually start a Dinero node:

```bash
# Navigate to the Dinero directory.
cd path/to/dinero

# Set up a Python virtual environment (Optional but recommended).
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate

# Install the required packages if needed.
pip install -r requirements.txt

# Manualy start the Denaro node on port 3006 or another specified port.
uvicorn dinero.node.main:app --port 3006

# To stop the node, press Ctrl+C in the terminal.
```

To exit a Python virtual environment, use the command:

```bash
deactivate
```

## Setup with Docker

```bash
make build
docker-compose up -d
```

## Sync Blockchain

To synchronize a node with the Denaro blockchain, send a request to the `/sync_blockchain` endpoint after starting your node:

```bash
curl http://localhost:3006/sync_blockchain
```

## Mining

**Dinero** adopts a Proof of Work (PoW) system for mining:

- **Block Hashing**:
  - Utilizes the sha256 algorithm for block hashing.
  - The hash of a block must begin with the last `difficulty` hexadecimal characters of the hash from the previously mined block.
  - `difficulty` can also have decimal digits, that will restrict the `difficulty + 1`st character of the derived sha to have a limited set of values.

    ```python
    from math import ceil

    difficulty = 6.3
    decimal = difficulty % 1

    charset = '0123456789abcdef'
    count = ceil(16 * (1 - decimal))
    allowed_characters = charset[:count]
    ```

- **Rewards**:
  - Block rewards decrease by half over time until they reach zero.
  - Rewards start at `100` for the initial `150,000` blocks, decreasing in predetermined steps until a final reward of `0.3125` for the `458,733`rd block.
  - After this, blocks do not offer a mining reward, but transaction fees are still applicable. A transaction may also have no fees at all.

## License
Dinero is released under the terms of the GNU Affero General Public License v3.0. See [LICENSE](LICENSE) for more information or goto https://www.gnu.org/licenses/agpl-3.0.en.html
