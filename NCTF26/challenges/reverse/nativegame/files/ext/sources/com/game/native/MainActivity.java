// Decompiled with jadx
package com.game.native;

import android.app.Activity;
import android.os.Bundle;

public class MainActivity extends Activity {
    static { System.loadLibrary("native"); }
    public native boolean checkFlag(byte[] flag, byte[] enc);

    protected void onCreate(Bundle b) {
        super.onCreate(b);
        // reads assets/enc.bin and calls checkFlag(userInput, enc)
    }
}
