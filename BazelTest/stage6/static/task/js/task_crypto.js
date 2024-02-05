const secretKey = 'YourSecretKey123'; // Replace this with your secret key

function decryptData(encryptedData) {
    var key = CryptoJS.enc.Utf8.parse(secretKey);
    var ciphertext = CryptoJS.enc.Base64.parse(encryptedData);

    // Get the IV by taking the first 16 bytes
    var iv = ciphertext.clone();
    iv.sigBytes = 16; // Set IV length to 16 bytes
    iv.clamp(); // Remove ciphertext leaving only IV'
    console.log("ciphertext", ciphertext)
    console.log("iv", iv)
    console.log("ciphertext", ciphertext)

    ciphertext.words.splice(0, 4); // Remove IV from ciphertext
    ciphertext.sigBytes -= 16; // Adjust ciphertext length
    console.log("ciphertext2", ciphertext)

    // Perform decryption
    var decrypted = CryptoJS.AES.decrypt({ ciphertext: ciphertext }, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7});

    const decryptedData = new Uint8Array(decrypted.sigBytes);
    for (let i = 0; i < decrypted.sigBytes; i++) {
        decryptedData[i] = decrypted.words[i >>> 2] >>> (24 - (i % 4) * 8) & 0xff;
    }

    return decryptedData;
}

async function encryptData(data) {
  console.log("data:", data)
  var key = CryptoJS.enc.Utf8.parse(secretKey);
  var iv = CryptoJS.lib.WordArray.random(16);
  var wordArray = CryptoJS.lib.WordArray.create(new Uint8Array(data));

  var encrypted = CryptoJS.AES.encrypt(wordArray, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });

   var res = iv.concat(encrypted.ciphertext).toString(CryptoJS.enc.Base64);

   console.log("res: ", res);

   return res;
}

