// Decompiled with jadx
package com.stashbox.app;

import android.app.Activity;
import android.os.Bundle;

public class MainActivity extends Activity {
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        String license = StringFog.unfog();
        // license is checked against the server; value not stored in cleartext
    }
}
