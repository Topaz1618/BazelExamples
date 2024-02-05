// JavaScript decryption using CryptoJS
const secretKey = 'YourSecretKey123'; // Replace this with your secret key

function decryptData(encryptedData) {
  const key = CryptoJS.enc.Utf8.parse(secretKey);

  // Decode the Base64 encoded string containing IV and ciphertext
  const encryptedDataBytes = CryptoJS.enc.Base64.parse(encryptedData);

  // Extract IV (first 16 bytes) and ciphertext
  const iv = encryptedDataBytes.clone();
  iv.sigBytes = 16;
  iv.clamp();

  const ciphertext = encryptedDataBytes.words.slice(4); // Remove IV (first 4 words)
  const encrypted = CryptoJS.lib.WordArray.create(ciphertext);

  // Decrypt using AES in CBC mode with PKCS7 padding
  const decrypted = CryptoJS.AES.decrypt({ ciphertext: encrypted, salt: '' }, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });

  // Convert the decrypted data to a string and return
  return decrypted.toString(CryptoJS.enc.Utf8);
}


async function encryptData(data) {
  const key = CryptoJS.enc.Utf8.parse(secretKey);

  // Generate a random IV (Initialization Vector)
  const iv = CryptoJS.lib.WordArray.random(16);

  // Encrypt the data using AES in CBC mode with PKCS7 padding
  const encrypted = CryptoJS.AES.encrypt(data, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });

  // Combine IV and ciphertext and encode as Base64
  return iv.concat(encrypted.ciphertext).toString(CryptoJS.enc.Base64);
}

// Example usage:
const plainText = 'Hello, World!';
encryptData(plainText).then(encryptedData => {
  console.log('Encrypted:', encryptedData);
});

// Example usage (use the encrypted data obtained from Python):
const encryptedDataFromPython = "pc27u8uFm0exib9wJ1iSLoa0VtbGD/cj9DCeBja5VXw="; // Replace with the actual encrypted data
const decryptedData = decryptData(encryptedDataFromPython);
console.log('Decrypted:', decryptedData);




