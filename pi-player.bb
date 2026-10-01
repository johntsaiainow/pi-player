SUMMARY = "Terminal MP3/FLAC Player with Cover Art support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://player.py"

# Depend only on core packages available in Poky/meta-oe
RDEPENDS:${PN} = " \
    python3-core \
    mpv \
"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/player.py ${D}${bindir}/pi-player

    # Set auto-execution on tty1 login
    install -d ${D}/root
    echo '[ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ] && exec pi-player' >> ${D}/root/.profile
}

FILES:${PN} += " \
    ${bindir}/pi-player \
    /root/.profile \
"
