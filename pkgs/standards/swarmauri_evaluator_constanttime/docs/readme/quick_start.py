import secrets
import time

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_constanttime import ConstantTimeEvaluator


class DummyProgram(IProgram):
    def diff(self, other: "IProgram"):
        return ()

    def apply_diff(self, diff):
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DummyProgram()


def insecure_compare(secret: bytes, guess: bytes) -> bool:
    for secret_byte, guess_byte in zip(secret, guess):
        if secret_byte != guess_byte:
            return False
        time.sleep(0.0001)
    return len(secret) == len(guess)


def make_input_pair() -> tuple[bytes, bytes]:
    return secrets.token_bytes(16), secrets.token_bytes(16)


def main() -> None:
    evaluator = ConstantTimeEvaluator()
    score, metadata = evaluator._compute_score(
        program=DummyProgram(),
        fn=insecure_compare,
        make_input_pair=make_input_pair,
        fixed_pair=(b"A" * 16, b"A" * 16),
        n_samples=20,
        iters_per=5,
    )

    print(f"Score: {score:.1f}")
    print(f"Constant time? {metadata['constant_time']}")
    print(f"t-statistic: {metadata['t_stat']:.2f}")
    print(f"Cliff's delta: {metadata['cliff_delta']:.3f}")

    assert metadata["constant_time"] is False


if __name__ == "__main__":
    main()
