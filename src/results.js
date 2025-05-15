const sampleFoods = [
  { id: 1, name: 'Margherita Pizza', image: "../Assets/blueberry.png", recipeLink: '#', orderLink: '#' },
  { id: 2, name: 'Sushi Platter',    image: 'Assets/sushi.jpg',       recipeLink: '#', orderLink: '#' },
  { id: 3, name: 'Chocolate Brownie', image: 'Assets/pancake.jpg',     recipeLink: '#', orderLink: '#' },
  { id: 4, name: 'Caesar Salad',     image: 'Assets/caesar.jpg',      recipeLink: '#', orderLink: '#' },
  { id: 5, name: 'Pad Thai',         image: 'Assets/padthai.jpg',     recipeLink: '#', orderLink: '#' },
  { id: 6, name: 'Avocado Toast',    image: 'Assets/avocadotoast.jpg',recipeLink: '#', orderLink: '#' }
];

let foods = [...sampleFoods];
const gridContainer = document.querySelector('.card-grid');
const moreBtn = document.getElementById('more-btn');

function renderCards() {
  gridContainer.innerHTML = '';
  foods.slice(0, 6).forEach(food => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <img src="${food.image}" alt="${food.name}">
      <div class="card-content">
        <h3>${food.name}</h3>
      </div>
      <div class="card-actions">
        <button class="btn btn-outline" onclick="window.open('${food.recipeLink}','_blank')">Recipe</button>
        <button class="btn btn-primary" onclick="window.open('${food.orderLink}','_blank')">Order Online</button>
      </div>
    `;
    gridContainer.appendChild(card);
  });
}

if (moreBtn) {
  moreBtn.addEventListener('click', () => {
    foods = foods.map(f => ({ ...f, id: f.id + foods.length, name: f.name + ' (Alt)' }));
    renderCards();
  });
}

document.addEventListener('DOMContentLoaded', renderCards);