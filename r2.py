from pyats.topology import loader

testbed = loader.load("testbed.yaml")
device = testbed.devices["R2"]

print("Connecting to R2...")
device.connect(log_stdout=True)
print("Connected successfully!")
