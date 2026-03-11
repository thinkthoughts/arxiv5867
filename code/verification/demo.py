from primorial_checks import PrimorialVerifier

v = PrimorialVerifier(alpha=24/25)

print("Trying one small test...")
actual, predicted, ratio = v.type_ii_sum(100000, 30)
print(f"Actual: {actual}")
print(f"Predicted: {predicted}")
print(f"Ratio: {ratio}")
print(f"Target 24/25 = 0.96")
