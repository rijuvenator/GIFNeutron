#!/bin/bash

# first few events
python EventDisplay.py  --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 172
python EventDisplay.py  --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 358
python EventDisplay.py  --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 448
python EventDisplay.py  --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 502
python EventDisplay.py  --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 556

python RecHitDisplay.py --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 172
python RecHitDisplay.py --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 358
python RecHitDisplay.py --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 448
python RecHitDisplay.py --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 502
python RecHitDisplay.py --list <(echo "3595") --file ../MakeHistosAndTree/test.root --cham 556
