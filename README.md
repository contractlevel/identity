# Contract Level Identity (CLID): A Decentralized Fuzzy Extractor

This project is being researched for the [vLEI Hackathon](https://www.gleif.org/en/newsroom/events/gleif-vlei-hackathon-2025), and is intended to address the critical need for absolute sybil-resistance by consensus.

## Set Up

### GLEIF Testnet Infrastructure

The [vLEI-trainings resource](https://github.com/gleIF-IT/vlei-trainings) is used for deploying GLEIF testnet infrastructure, but is not included in this repo.

Open Docker:

```
open -a Docker
```

Deploy GLEIF testnet infra:

```
./vlei-trainings/deploy.sh
```

Terminate deployed GLEIF testnet infra:

```
./vlei-trainings/stop.sh
```

### CLID Fuzzy Signer

Create virtual environment (skip this step if already done):

```
python3 -m venv .venv
```

Run virtual environment:

```
source .venv/bin/activate
```

Install dependencies:

```
pip install -e . # during development
pip install . # for reproducible build
```

Terminate virtual environment:

```
deactivate
```

## Run the current demo

Inside virtual environment:

```
python3 fuzzy_signer/make_ntid.py
```

When running the above command, you will be prompted to input a phrase for keystrokes. The application will monitor your keystrokes, extract and process the biometric data to "enroll" in the current system.

You will be prompted a second time to enter the phrase again. This time the key extracted from your keystroke biometric data will be reproduced by the fuzzy extractor and used to create and control an Autonomic Identifier (AID).

You will then be prompted to enter the phrase for a third and final time. This is to confirm that the transient key derived from your biometric data reproduces the same stable, deterministic AID.
