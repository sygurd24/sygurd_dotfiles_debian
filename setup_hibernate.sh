#!/bin/bash
set -e

echo ">>> Setting up Hibernation (Suspend-to-Disk)..."

# Detect RAM
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
RECOMMENDED_SWAP=$((TOTAL_RAM_GB + 1))

echo "Detected RAM: ${TOTAL_RAM_GB}GB"
echo "For hibernation, swap size should be at least equal to RAM size."
echo "Recommended: ${RECOMMENDED_SWAP}GB"

read -p "Enter desired swap size in GB (default: ${RECOMMENDED_SWAP}): " USER_SWAP
SWAP_SIZE=${USER_SWAP:-$RECOMMENDED_SWAP}

echo ">>> Selected Swap Size: ${SWAP_SIZE}GB"

# 1. Create Swapfile
if [ -f /swapfile ]; then
    echo "Existing /swapfile found. Turning it off..."
    swapoff /swapfile || true
    rm /swapfile
fi

echo ">>> Creating ${SWAP_SIZE}GB Swapfile (this may take a moment)..."
dd if=/dev/zero of=/swapfile bs=1G count="$SWAP_SIZE" status=progress
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

echo ">>> Updating /etc/fstab..."
# Verify fstab doesn't already have it
if ! grep -q "/swapfile" /etc/fstab; then
    echo "/swapfile none swap sw 0 0" >> /etc/fstab
fi

# 2. Configure GRUB
echo ">>> Configuring GRUB..."
# Get UUID of root partition
ROOT_UUID=$(findmnt -no UUID -T /swapfile)
# Get Offset of swapfile
RESUME_OFFSET=$(filefrag -v /swapfile | awk 'NR==4{print $4}' | tr -d .)

if [ -z "$ROOT_UUID" ] || [ -z "$RESUME_OFFSET" ]; then
    echo "Error: Could not determine UUID or Offset."
    exit 1
fi

echo "UUID: $ROOT_UUID"
echo "Offset: $RESUME_OFFSET"

# Add resume params to GRUB_CMDLINE_LINUX_DEFAULT
# We use sed to append if not present
if grep -q "resume=" /etc/default/grub; then
    echo "GRUB already has resume parameters. Please check /etc/default/grub manually if you want to update them."
    echo "Proposed: resume=UUID=$ROOT_UUID resume_offset=$RESUME_OFFSET"
else
    sed -i "s/GRUB_CMDLINE_LINUX_DEFAULT=\"/GRUB_CMDLINE_LINUX_DEFAULT=\"resume=UUID=$ROOT_UUID resume_offset=$RESUME_OFFSET /" /etc/default/grub
    echo ">>> Updating GRUB config..."
    update-grub
fi

# 3. Update Initramfs
echo ">>> Updating initramfs (to include resume capability)..."
# Ensure initramfs-tools has resume config
if [ ! -f /etc/initramfs-tools/conf.d/resume ]; then
    echo "RESUME=UUID=$ROOT_UUID" > /etc/initramfs-tools/conf.d/resume
    echo "resume_offset=$RESUME_OFFSET" >> /etc/initramfs-tools/conf.d/resume
fi
update-initramfs -u

# 4. Configure Logind
echo ">>> Configuring logind to Hibernate on lid close..."
sed -i 's/#HandleLidSwitch=suspend/HandleLidSwitch=hibernate/' /etc/systemd/logind.conf
sed -i 's/HandleLidSwitch=suspend/HandleLidSwitch=hibernate/' /etc/systemd/logind.conf

echo ">>> DONE! Please restart your computer to apply changes."
