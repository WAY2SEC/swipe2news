// Swipe2News service worker for push alerts: OneSignal + the same offline support as sw.js.
try { importScripts("https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.sw.js"); } catch (e) {}
importScripts("sw.js");
