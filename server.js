require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { GoogleAuth } = require("google-auth-library");
const path = require("path");
const app = express();
const port = process.env.PORT || 3000;

app.use(cors());

// Path to the service account key file
const keyFilePath = path.join(__dirname, process.env.KEY_FILE_PATH);

async function getAccessToken() {
  try {
    const auth = new GoogleAuth({
      keyFile: keyFilePath,
      scopes: ["https://www.googleapis.com/auth/cloud-platform"],
    });

    const client = await auth.getClient();
    const accessToken = await client.getAccessToken();
    return accessToken.token;
  } catch (error) {
    console.error("Error fetching access token:", error);
    throw new Error("Failed to fetch access token");
  }
}

// API to serve the access token
app.get("/getAccessToken", async (req, res) => {
  try {
    const token = await getAccessToken();
    res.json({ token });
  } catch (error) {
    res.status(500).send("Error fetching token");
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
