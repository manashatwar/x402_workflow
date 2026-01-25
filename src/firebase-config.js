// Firebase Configuration
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyArWADWJhLNpP8s35VXEgVvVnZood_qm3Q",
  authDomain: "x402-7d715.firebaseapp.com",
  projectId: "x402-7d715",
  storageBucket: "x402-7d715.firebasestorage.app",
  messagingSenderId: "1066442701020",
  appId: "1:1066442701020:web:209dba7b72c9b599a0dc19",
  measurementId: "G-Q7F61FJD42"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const analytics = getAnalytics(app);

export { auth, db, analytics };
