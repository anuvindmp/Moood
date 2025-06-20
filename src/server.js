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
