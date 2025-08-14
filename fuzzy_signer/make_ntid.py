"""
make_ntid.py  ·  KERI 1.3  ·  Python 3.13
This script is used to create a non-transferable AID (only the inception event).
NTID stands for Non-Transferable Identifier.
----------------------------------------------------------
• Builds a non-transferable AID (only the inception event).
• The signing key is derived on-the-fly from the fuzzy extractor.
• Nothing is written to disk (temp=True Habitat store).
• Non-transferable AIDs are self-contained (no witnesses needed).
----------------------------------------------------------
Prereqs
  • fuzzy_signer.py in the same folder (defines reproduce())
"""

from keri.app import habbing
from keri.core.signing import Signer              # Ed25519 key helper
from fuzzy_signer import enroll, reproduce        # deterministic 32-byte seed

# -----------------------------------------------------------------------
# 1. Open an in-memory Habitat store (temp=True → no ~/.keri folder)
# -----------------------------------------------------------------------
with habbing.openHby(name="bio_demo", temp=True) as hby:

    # 2. First, enroll to set up the fuzzy extractor
    print("🎯 Step 1: Enrollment")
    seed1, _ = enroll()  # This will capture the enrollment keystrokes
    print(f"🔑 Enrollment seed: {seed1}")
    
    # 3. Now reproduce the seed and wrap it as an Ed25519 Signer
    print("\n🔄 Step 2: First authentication")
    seed        = reproduce()                     # bytes, same every run
    signer      = Signer(raw=seed, transferable=False)
    secret_qb64 = signer.qb64                     # base64 secret for KERI

    print(f"Auth seed: {seed}")

    # 4. Create the Habitat with that single secret (new API uses 'secrecies')
    hab = hby.makeHab(
        name="myNTID",
        transferable=False,                       # Non-transferable AID
        secrecies=[[secret_qb64]],                # list-of-lists form
    )

    print(f"\n✅  Deterministic AID : {hab.pre}")

    # 5. Non-transferable AIDs are self-contained - no witnesses needed
    print("📤  Non-transferable AID created successfully.\n")

    # ── 6. sanity-check: call reproduce() again and confirm same AID ─────
    print("🔄 Step 3: Second authentication (verification)")
    seed2   = reproduce()                               # fresh noisy sample
    signer2 = Signer(raw=seed2, transferable=False)
    aid2    = signer2.verfer.qb64                       # A-prefix = public key
    if aid2 == hab.pre:
        print(f"\n🔁  Second reproduce() : {aid2} → SAME AID ✔")
    else:
        print("❌  Second reproduce() produced a DIFFERENT AID!", aid2)

    # 7. Non-transferable AIDs are self-contained – no witnesses needed
    print("📤  Non-transferable AID deterministically reproduced successfully.\n")
