<h1 align="center">Offensive Subdomains Wordlists Creator</h1>

<h1 align="center">oswc.sh</h1>

This bash script is designed to gather subdomain data from various reputable sources and merge them together to create multiple wordlists, each organized by different subdomain levels, and make a master subdomains wordlist merging all different levels subdomains wordlists. This makes a very effective and massive wordlist consisting of `66 million +` subdomains, that can be further used in the subdomain brute-forcing process by security researchers and bug hunters.

## Installation
```
wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/main/Subdomains-Wordlists/oswc.sh
```
```
chmod +x oswc.sh
```

## Usage
```
./oswc.sh
```
Saving results in specific directory, by default it saves results in present working directory
```
./oswc.sh --output /opt/wordlists
```

## Sample Output
```
first_level_subdomains_wordlist.txt
-----------------------------------
sub1
sub2
sub3

second_level_subdomains_wordlist.txt
-----------------------------------
sub1.sub
sub2.sub
sub3.sub

Until ninth_and_above_level_subdomains_wordlist.txt...
```

## Tools Used and References

- [Duplicut](https://github.com/nil0x42/duplicut) - required

- [Notify](https://github.com/projectdiscovery/notify) - optional

<h1 align="center">oswc_dsieve.sh</h1>

This script serves the same purpose as the above script, but uses different tools such as `dsieve` and `unfurl` instead of `awk` and `duplicut` to achieve the same result. There is no difference in the output produced by both scripts. The above script, which uses `awk` and `duplicut`, is more suitable for systems with low RAM compared to this script.

## Installation
```
wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/main/Subdomains-Wordlists/oswc_dsieve.sh
```
```
chmod +x oswc_dsieve.sh
```

## Usage
```
./oswc_dsieve.sh
```
Saving results in specific directory, by default it saves results in present working directory
```
./oswc_dsieve.sh --output /opt/wordlists
```

## Sample Output
```
first_level_subdomains_wordlist.txt
-----------------------------------
sub1
sub2
sub3

second_level_subdomains_wordlist.txt
-----------------------------------
sub1.sub
sub2.sub
sub3.sub

Until ninth_and_above_level_subdomains_wordlist.txt...
```

## Tools Used and References

- [Dsieve](https://github.com/trickest/dsieve) - required

- [Unfurl](https://github.com/tomnomnom/unfurl) - required

- [Notify](https://github.com/projectdiscovery/notify) - optional

## Special Thanks and Resources

- [SecLists](https://github.com/danielmiessler/SecLists/)

- [Jason Haddix](https://github.com/jhaddix)

- [six2dez](https://github.com/six2dez)

- [Assetnote](https://wordlists.assetnote.io)

- [Script kiddie hacker](https://github.com/script-kiddie-hacker)

- [Trickest](https://github.com/trickest)
