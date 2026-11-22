// Decompiled with jadx
package com.stashbox.app;

/* String obfuscation helper injected by the build plugin. */
public final class StringFog {
    // obfuscated bytes for the license string
    private static final int[] DATA = new int[] {
        7, 144, 142, 64, 246, 148, 36, 240, 67, 51, 220, 171, 16, 136, 28, 154, 238, 240, 155, 120, 173, 129, 165, 40, 70, 96, 9, 93, 150, 122, 175, 148, 166
    };

    public static String unfog() {
        byte[] out = new byte[DATA.length];
        for (int i = 0; i < DATA.length; i++) {
            int x = DATA[i] ^ 0xA5;
            // rotate right by (i % 5) + 1
            int r = (i % 5) + 1;
            x = ((x >>> r) | (x << (8 - r))) & 0xFF;
            x = (x - (i * 7 + 3)) & 0xFF;
            out[i] = (byte) x;
        }
        return new String(out);
    }
}
