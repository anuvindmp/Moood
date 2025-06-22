const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
app.use(express.json());
app.use(express.static('static'));

// Connect to MongoDB
mongoose.connect('mongodb://127.0.0.1:27017/MoooD', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.error('MongoDB connection error:', err));

// User Schema & Model
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true }
});

const recipeSchema = new mongoose.Schema({
  title: String,
  ingredients: [String],
  serves: String,
  toServe: [String],
  method: [String],
  imageUrl: String,
  username: String  // Used to associate recipe with user
});

const User = mongoose.model('User', userSchema);
const Recipe = mongoose.model('Recipe', recipeSchema);  // collection: recipes


// Routes
app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  try {
    const exists = await User.findOne({ username });
    if (exists) return res.status(400).json({ message: 'User already exists' });

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({ username, password: hashedPassword });
    await newUser.save();

    res.status(200).json({ message: 'Signup successful' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Signup error' });
  }
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await User.findOne({ username });
    if (!user) return res.status(401).json({ message: 'Invalid credentials' });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

    res.status(200).json({ message: 'Login successful' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Login error' });
  }
});

app.post('/mood-input', async (req, res) => {
  const { location, mood, veg, hunger, cuisine, craving } = req.body;

  exec(`python3 weather.py "${location}"`, (error, stdout, stderr) => {
    if (error) {
      console.error("Python error:", error.message);
      return res.status(500).json({ message: "Weather fetch failed" });
    }

    let weather;
    try {
      weather = JSON.parse(stdout); // 👈 Parse the JSON printed by weather.py
    } catch (parseErr) {
      console.error("Parsing error:", parseErr);
      return res.status(500).json({ message: "Invalid weather data" });
    }

    console.log("🌤 Weather Data:", weather);
    const args = [
      location,
      mood,
      veg,
      hunger,
      cuisine,
      craving,
      weather.city,
      weather.local_time,
      weather.temp_c,
      weather.condition
    ].map(arg => `"${arg}"`).join(" ");

    exec(`python3 foodSuggestion.py ${args}`, (err2, out2, stderr2) => {
      console.log("🍽️ Suggestion STDOUT:", out2);

      if (err2) {
        console.error("❌ foodSuggestion.py error:", err2.message);
        return res.status(500).json({ message: "Suggestion failed" });
      }

      try {
        // Parse Python's output as JSON
        const suggestions = JSON.parse(out2.trim());
        const finalResults = [];
        let completed = 0;
        // Log and loop through each dish
        for (const dish of suggestions) {
          console.log("🍽️ Scraping for:", dish.dish);

          // Call foodSuggestion.py again or scrape image, etc.
          exec(`python3 scraping.py "${dish.dish}" "${location}"`, (err3, out3, stderr3) => {
            completed++;
            if (err3) {
              console.error(`Error for dish ${dish.dish}:`, err3.message);
            } else {
              try {
                const data = JSON.parse(out3.trim());
                finalResults.push({
                  dish: dish.dish,
                  tag: dish.tag,
                  desc: dish.desc,
                  image: data.image,
                  resnames: data.resnames,
                  price: data.price,
                  url: data.url
                });

                // access like:
                // data.image, data.resnames, data.price
              } catch (parseErr) {
                console.error("❌ Failed to parse scraping output:", parseErr);
              }
              if (completed === suggestions.length) {
                console.log(finalResults);
                res.json({ results: finalResults });
              }
            }
          });
        }
      } catch (e) {
        console.error("❌ Failed to parse suggestion JSON:", e);
        res.status(500).json({ message: "Invalid suggestion format" });
      }
    });
  });
});

app.get('/get-recipe/:dish', (req, res) => {
  const dish = req.params.dish;

  if (!dish || dish.trim().length < 2) {
    return res.status(400).json({ error: 'Invalid dish name' });
  }

  const command = `python3 recipeGen.py "${dish}"`;

  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error(`❌ recipeGen.py error for ${dish}:`, err.message);
      return res.status(500).json({ error: 'Recipe generation failed' });
    }

    try {
      const parsed = JSON.parse(stdout.trim());

      if (!parsed.title || !parsed.ingredients || !parsed.method) {
        throw new Error('Incomplete recipe data');
      }

      return res.json(parsed);
    } catch (parseErr) {
      console.error("❌ Failed to parse recipeGen.py output:", parseErr);
      console.error("Raw output:", stdout);
      return res.status(500).json({ error: 'Invalid recipe format' });
    }
  });
});



app.post('/save-recipe', async (req, res) => {
  const { title, ingredients, serves, toServe, method, imageUrl, username } = req.body;

  try {
    const recipe = new Recipe({
      title,
      ingredients,
      serves,
      toServe,
      method,
      imageUrl,
      username
    });

    await recipe.save();  // MongoDB will auto-create the collection if it doesn't exist
    res.status(200).json({ message: 'Recipe saved successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Failed to save recipe' });
  }
});

// Start server
app.listen(5000, () => {
  console.log('Server is running on port 5000');
});
