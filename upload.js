const admin = require('firebase-admin');
const axios = require('axios');

// Firebase Admin SDK Setup
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const JSON_URL = 'https://raw.githubusercontent.com/KoHtunDevelop/daryl-thai-lottery/refs/heads/main/lotto.json';

async function uploadLotteryData() {
  try {
    // 1. GitHub ကနေ Data ဖတ်ယူခြင်း
    const response = await axios.get(JSON_URL);
    const lotteryData = response.data; // ဤနေရာတွင် array ဖြစ်သည်

    const batch = db.batch();

    lotteryData.forEach((draw) => {
      // Document ID ကို Date နဲ့ထားခြင်းက ပိုရှုပ်ထွေးမှုကို သက်သာစေသည်
      // Draw တစ်ခုချင်းစီအတွက် unique ID တစ်ခုယူပါ
      const docRef = db.collection('lottery_results').doc();

      // သင်လိုချင်တဲ့ Structure အတိုင်း ပုံဖော်ခြင်း
      const formattedData = {
        date: draw.date, // dd-Mmm-yyyy
        results: draw.results.map(res => ({
          prize: res.prize,
          ticket: res.ticket // ticket က array လည်းဖြစ်နိုင်၊ string လည်းဖြစ်နိုင်သည်
        })),
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      };

      batch.set(docRef, formattedData);
    });

    // 2. Firestore ထဲသို့ အားလုံးတစ်ပြိုင်နက် ပို့ခြင်း
    await batch.commit();
    console.log('✅ Data အားလုံးကို Firestore ထဲသို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ။');

  } catch (error) {
    console.error('❌ အမှားအယွင်းရှိခဲ့သည်:', error);
  }
}

uploadLotteryData();
  
