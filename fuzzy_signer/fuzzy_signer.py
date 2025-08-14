# bio_demo/fuzzy_signer.py
from fuzzy_extractor import FuzzyExtractor
from keri.core import coring
from keri.core.signing import Siger as Sig
from bio_input import capture_enroll, capture_auth  # same folder

HAM_ERR = 10  # tune after measuring noise

# Global variables to store the fuzzy extractor and helper data
fe = FuzzyExtractor(length=32, ham_err=HAM_ERR)
HELPER = None

# 1) Enrollment: capture keystrokes -> FE.generate()
def enroll():
    """External enrollment function that can be called from other modules"""
    global HELPER
    _enrol_u8 = capture_enroll()                  # np.uint8[32]
    SEED, HELPER = fe.generate(_enrol_u8)        # SEED is not stored; HELPER kept in RAM
    print("✅ Enrollment completed successfully")
    return SEED, HELPER

# 2) Reproduction per use
def reproduce() -> bytes:
    if HELPER is None:
        raise ValueError("Must call enroll() first before reproduce()")
    auth_u8 = capture_auth()
    seed = fe.reproduce(auth_u8, HELPER)
    if seed is None:
        raise ValueError("Too much noise; try again.")
    return seed  # 32 bytes

# 3) Minimal signer wrapper for KERI ≥ 1.3
class FuzzySigner:
    def __init__(self, rep_fn=reproduce, index: int = 0):
        self.rep_fn = rep_fn
        self.index = index

    def sign(self, ser: bytes, index: int | None = None) -> Sig:
        sk = coring.Signify(self.rep_fn())     # derive Ed25519 keypair from seed
        sig = sk.sign(ser)
        return Sig(sig=sig, verkey=sk.verkey, index=index if index is not None else self.index)
