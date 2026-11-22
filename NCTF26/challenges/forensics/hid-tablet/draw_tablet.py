import matplotlib.pyplot as plt
import struct

x_vals, y_vals = [], []

with open("hid_data.txt", "r") as f:
    for line in f:
        line = line.strip().replace(":", "")
        if len(line) != 16:
            continue
        data = bytes.fromhex(line)
        status, x, y, pressure = struct.unpack("<BHHHx", data)
        if status == 1:
            x_vals.append(x)
            y_vals.append(y)

print(f"Points extraits : {len(x_vals)}")
plt.figure(figsize=(16, 6))
plt.scatter(x_vals, y_vals, s=1, c="black")
plt.gca().invert_yaxis()
plt.axis("equal")
plt.savefig("flag.png", dpi=300, bbox_inches="tight")
plt.show()
