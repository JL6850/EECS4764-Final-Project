document.addEventListener('DOMContentLoaded', () => {
    const zones = document.querySelectorAll('.zone');
    zones.forEach((zone, index) => {
        const id = index + 1;
        zone.setAttribute('data-id', id);

        const menu = document.createElement('div');
        menu.className = 'menu';
        menu.innerHTML = `
            <button onclick="viewCard(${id})">放大查看</button>
            <button onclick="addCardToZone(${id})">放入卡牌</button>
            <button onclick="discardCard(${id})">丢弃卡牌</button>
            <button onclick="setAttackState(${id})">攻击状态</button>
            <button onclick="setDefenseState(${id})">防御状态</button>
        `;
        zone.appendChild(menu);
    });
});

function viewCard(zoneId) {
    const zone = document.querySelector(`.zone[data-id='${zoneId}']`);
    if (zone) {
        const img = zone.querySelector('img');
        if (img) {
            const modal = document.getElementById('imageModal');
            const modalImage = document.getElementById('modalImage');
            const modalText = document.getElementById('modalText');
            modal.style.display = 'block';
            modalImage.src = img.src;
            modalText.textContent = img.getAttribute('data-text');
        } else {
            alert(`区域 ${zoneId} 没有图片可查看！`);
        }
    } else {
        alert(`找不到区域 ${zoneId}！`);
    }
}

function addCardToZone(zoneId) {
    const zone = document.querySelector(`.zone[data-id='${zoneId}']`);
    if (zone) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = '新卡牌';
                img.setAttribute('data-text', '这是一张新的卡牌');
                img.style.cursor = 'pointer';
                zone.appendChild(img);
                // alert(`卡牌已放入区域 ${zoneId}`);
            }
        });
        fileInput.click();
    } else {
        alert(`未找到区域 ${zoneId}`);
    }
}

function discardCard(zoneId) {
    const zone = document.querySelector(`.zone[data-id='${zoneId}']`);
    if (zone) {
        const img = zone.querySelector('img');
        if (img) {
            zone.removeChild(img);
            // alert(`区域 ${zoneId} 的卡牌已丢弃`);
        } else {
            alert(`区域 ${zoneId} 没有卡牌可丢弃！`);
        }
    }
}

function setAttackState(zoneId) {
    const zone = document.querySelector(`.zone[data-id='${zoneId}']`);
    if (zone) {
        const img = zone.querySelector('img');
        if (img) {
            img.style.transform = 'rotate(0deg)';
            // alert(`区域 ${zoneId} 设置为攻击状态`);
        } else {
            alert(`区域 ${zoneId} 没有卡牌`);
        }
    }
}

function setDefenseState(zoneId) {
    const zone = document.querySelector(`.zone[data-id='${zoneId}']`);
    if (zone) {
        const img = zone.querySelector('img');
        if (img) {
            img.style.transform = 'rotate(90deg)';
            // alert(`区域 ${zoneId} 设置为防御状态`);
        } else {
            alert(`区域 ${zoneId} 没有卡牌`);
        }
    }
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
}

window.onclick = function (event) {
    const modal = document.getElementById('imageModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};


let lastData = null; // 保存上一次的数据

async function fetchLatestData() {
    try {
        const response = await fetch('/api/data', { method: 'GET' });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        // 解构嵌套的 data 属性
        if (result.data) {
            console.log("New data received:", result.data); // Debug log
            handleAction(result.data); // 将解构后的 data 传递给 handleAction
        } else {
            console.error("Invalid JSON format:", result);
        }
    } catch (error) {
        console.error("Error fetching data:", error.message);
    }
}

// Function to handle different actions
function handleAction(data) {
    console.log("Received data in handleAction:", data); // Print the entire JSON data
    const { action, location, card_id } = data;

    switch (action) {
        case "Summon":
            summonCard(location, card_id);
            break;

        case "Discard":
            deleteCard(location, card_id);
            break;
        // Add more cases for other actions
        default:
            console.error("Unknown action:", action);
    }
}

function clearCardInZone(targetZone) {
    const card = targetZone.querySelector('img'); // 选择卡牌元素
    if (card) {
        targetZone.removeChild(card); // 仅移除卡牌
    } else {
        console.log("No card found in the target zone.");
    }
}

function summonCard(location, card_id) {
    const zones = document.querySelectorAll('.zone'); // 获取所有区域
    const targetZone = zones[location - 1]; // 获取指定区域（1-based index）

    if (targetZone) {
        clearCardInZone(targetZone); // 仅移除旧卡牌

        // 添加新卡牌
        const card = document.createElement('img');
        card.src = `/data/card/${card_id}.jpg`; // 假设卡牌图片路径
        card.alt = `Card ${card_id}`;
        card.className = 'card'; // 为新卡牌添加样式类

        targetZone.appendChild(card); // 将新卡牌插入到区域
    } else {
        console.error(`Invalid location: ${location}`);
    }
}

function deleteCard(location) {
    const zones = document.querySelectorAll('.zone'); // 获取所有区域
    const targetZone = zones[location - 1]; // 获取指定区域（1-based index）

    if (targetZone) {
        clearCardInZone(targetZone); // 仅卡牌
    } else {
        console.error(`Invalid location: ${location}`);
    }
}



// Automatically refresh data every 2 seconds
setInterval(fetchLatestData, 2000);

// Fetch data immediately after the page loads
document.addEventListener('DOMContentLoaded', fetchLatestData);
