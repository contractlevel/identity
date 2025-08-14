"""
Fuzzy extract key and sign a message
- generate()
- reproduce()
- sign()
"""

"""
Enrolment:
1. Capture keystrokes (biometric input)
2. Process biometric input into format for fuzzy extractor
3. Use Reed-Solomon error correction to extract (c) consistency
4. Hash(c) to get uniqueId
5. Compare H(c) to uniqueIds stored in IPFS
6. If match, reject enrolment
7. Else store uniqueId in IPFS - should be shared later on
8. Fuzzy extracted key signs enrolment message
9. Helper data is given to user to store in a secure location
"""