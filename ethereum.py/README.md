# ethereum.py
ethereum.py is a Python Ethereum blockchain client that allows transactions to be sent to the blockchain via a REST API or a NATS subscriber.  ethereum.py works with the EligibilityCheck.sol smart contract, which stores FHIR resources on a Ethereum private network and provides coverage eligibility decisions based on the stored FHIR resources.

## Pre-requisites
- [Python 3.8 or higher](https://www.python.org/downloads/mac-osx/) for runtime/coding support
- [Pipenv](https://pipenv.pypa.io) for Python dependency management  
- [Docker Compose 1.28.6 or higher](https://docs.docker.com/compose/install/) for a local container runtime
- [Postman](https://www.postman.com/downloads/) to send HTTP requests to ethereum.py

The Ethereum client requires an Ethereum private network to connect to. If you don't have an Ethereum private network and would like to use Truffle + Ganache on your local machine, you can follow the instructions in the "Test with Truffle + Ganache" section.

## Clone the repositories
Clone the repositories - one for the smart contract and one for the Ethereum client:
```shell
git clone https://github.com/LinuxForHealth/connect-clients.git
git clone https://github.com/LinuxForHealth/connect-contracts.git
```
The connect-contracts/ethereum/eligibility project contains the EligibilityCheck.sol solidity contract which stores FHIR-R4 resources in the blockchain & renders eligibility decisions.  Deploy this contract to your Ethereum private network, or follow the instructions in the next section to deploy it locally using Truffle + Ganache.

## Test with Truffle + Ganache

### Set up a local environment
To test with a local Ethereum private network using Truffle and Ganache, first install both tools:
- [Truffle](https://www.trufflesuite.com/docs/truffle/getting-started/installation) for contract deployment
- [Ganache](https://www.trufflesuite.com/ganache) for a one-click local Ethereum network

### Start Ganache
Start the Ganache application and click "QuickStart".  This gives you a one-click local Ethereum network.  In the UI, click on the "Blocks" tab for a helpful view of blocks as they are added to the blockchain.

### Deploy the contract
Deploy the EligibilityCheck.sol contract to Ganache using Truffle, from the connect-contracts repo:
```shell
cd connect-contracts/ethereum/eligibility
truffle migrate
```
Note the value for contract address in the output under deploy_contracts.js.
```shell
2_deploy_contracts.js
=====================

   Replacing 'EligibilityCheck'
   ----------------------------
   > transaction hash:    0x5c22711e885ff81738e1bb3bf194752fb4c43104e97f70025d4871ec9663f960
   > Blocks: 0            Seconds: 0
   > contract address:    0x7Bad280884c907bBf3955c21351ce41122aB88eB
```
Update `ETHEREUM_CONTRACT_ADDRESS` in ethereum.py/.env to include the contract address:
```shell
ETHEREUM_NETWORK_URI=http://localhost:7545
ETHEREUM_CONTRACT_ADDRESS=0x7Bad280884c907bBf3955c21351ce41122aB88eB
```

### Start the Ethereum client
Start the Ethereum client from the command line from the LinuxForHealth connect-clients repo:
```shell
cd connect-clients/ethereum.py
pip install --upgrade pip
pipenv sync --dev
pipenv run ethereum
```

### Send data to the Ethereum client
To test the Ethereum client, use the REST calls from connect-clients/ethereum.py/LFH-Ethereum-Client.postman_collection.  Load the collection into Postman, then populate the blockchain by sending FHIR resources to the Ethereum client using the `Create Patient`, `Create Coverage` and `Create Insurer Organization` messages.  Watch the blocks appear in the blockchain using the Ganache UI.

With that data stored in the blockchain, you can now send a FHIR CoverageEligibilityRequest message (`Create CoverageEligibilityRequest`) and see the FHIR CoverageEligibilityResponse in the Ethereum client output.

## Using the Ethereum client with LinuxForHealth connect

### Set up a local environment
Follow the instructions to clone and configure [LinuxForHealth connect](https://github.com/LinuxForHealth/connect).  

LinuxForHealth connect includes a docker-compose.yml file containing the `ethereum-client` service, which is the ethereum.py project.  By default, ethereum-client will connect to your local Ganache blockchain, but it can be configured via environment variables.  In particular, you must replace the docker-compose.yml ETHEREUM_CONTRACT_ADDRESS value with the contract address from the `truffle migrate` step.
```shell
  ethereum-client:
    profiles: ["ethereum"]
    networks:
      - main
    image: linuxforhealth/ethereum-client:0.1.0
    environment:
      ETHEREUM_CA_PATH: /usr/local/share/ca-certificates
      ETHEREUM_RATE_LIMIT: 5/second
      ETHEREUM_CONTRACT_ADDRESS: "0x7Bad280884c907bBf3955c21351ce41122aB88eB"
    ports:
      - "5100:5100"
```
To connect to a different RPC server address, set ETHEREUM_NETWORK_URI in the docker-compose.yml section above. The default is "http://host.docker.internal:7545" for connecting from MacOS to the Ganache RPC server on localhost:7545 from inside a docker container.

### Start LinuxForHealth connect with the Ethereum client
To start the Ethereum client with connect, use the profile "ethereum", starting from the LinuxForHealth connect repo:
```shell
cd connect
docker-compose --profile deployment --profile ethereum up -d
```

### Test the ethereum-client Service
You can now test sending the same data as in the "Send data to the Ethereum client" section, but send it to LinuxForHealth on the connect port (5000) instead of the Ethereum client port (5100).  

In this scenario, LinuxForHealth emits a data synchronization message that's received by the ethereum-client service (the ethereum.py client contains both a FastAPI REST server and a NATS messaging client).  When the sync message is received, ethereum-client sends the message's data payload to the blockchain.

To see the CoverageEligibilityResponse, view the docker log for ethereum-client:
```shell
docker logs connect_ethereum-client_1
```
