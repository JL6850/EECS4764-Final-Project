// 初始化页面和功能版
document.addEventListener('DOMContentLoaded', () => {
    const zones = document.querySelectorAll('.zone');
    zones.forEach((zone, index) => {
        const id = index + 1;
        zone.setAttribute('data-id', id);

        // 找到当前 .zone 下的 <span> 或创建新的 <span> 元素
        let span = zone.querySelector('span');
        if (!span) {
            // 如果没有 <span>，创建一个新的
            span = document.createElement('span');
            zone.appendChild(span);
        }

        // 显示 ID
        span.textContent += ` (ID: ${id})`;
        const menu = document.createElement('div');
        menu.className = 'menu';
        menu.innerHTML = `
            <button onclick="viewCard(${id})">View Card</button>
            <button onclick="addCardToZone(${id})">Add to Zone</button>
            <button onclick="deleteCard(${id})">Discard Card</button>
            <button onclick="setAttackState(${id})">Attack Mode</button>
            <button onclick="setDefenseState(${id})">Defense Mode</button>
        `;
        zone.appendChild(menu);
    });
});

function getZoneById(zoneId) {
    return document.querySelector(`.zone[data-id='${zoneId}']`);
}

function viewCard(zoneId) {
    // 判断是否为墓地
    if (zoneId === 14) {
        viewGraveyard(); // 如果是墓地，调用查看墓地的逻辑
        return;
    }
    const zone = getZoneById(zoneId);
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
            alert(`No image available to view in zone ${zoneId}!`);
        }
    } else {
        alert(`Zone ${zoneId} not found!`);
    }
}

function showLargeImage(imageSrc, description) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalCaption = document.getElementById('modalCaption');

    // 设置图片和描述
    modalImage.src = imageSrc;
    modalCaption.textContent = description;

    // 显示弹窗并添加动画效果
    modal.classList.add('show');
}


function viewGraveyard() {
    const graveyardModal = document.getElementById('graveyardModal');
    const cardContainer = document.getElementById('graveyardCardContainer');
    const largeImageContainer = document.getElementById('graveyardLargeImageContainer');

    // 清空内容
    cardContainer.innerHTML = '';
    largeImageContainer.innerHTML = '<p class="empty-message">Click a card to view it here!</p>';

    if (graveyardCards.length === 0) {
        // 如果墓地为空，显示提示信息
        cardContainer.innerHTML = '<p class="empty-message">Graveyard is empty!</p>';
    } else {
        // 动态生成墓地卡牌
        graveyardCards.forEach((cardSrc, index) => {
            const cardImg = document.createElement('img');
            cardImg.src = cardSrc;
            cardImg.alt = `Graveyard Card ${index + 1}`;
            cardImg.className = 'graveyard-card';

            // 点击卡牌显示放大图
            cardImg.addEventListener('click', () => {
                largeImageContainer.innerHTML = ''; // 清空右侧内容
                const largeImg = document.createElement('img');
                largeImg.src = cardSrc;
                largeImg.alt = `Graveyard Card ${index + 1}`;
                largeImageContainer.appendChild(largeImg);
            });

            cardContainer.appendChild(cardImg);
        });
    }

    // 显示墓地模态框
    graveyardModal.style.display = 'block';
}

function closeGraveyardModal() {
    const graveyardModal = document.getElementById('graveyardModal');
    graveyardModal.style.display = 'none';
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
                const fileNameWithExtension = file.name; // 完整文件名，例如 "43227.jpg"
                const fileName = fileNameWithExtension.split('.')[0]; // 提取数字部分，去掉后缀
                img.src = URL.createObjectURL(file);
                img.alt = '新卡牌';
                img.setAttribute('data-text', '这是一张新的卡牌');
                img.style.cursor = 'pointer';
                img.className = 'img'; // 为新卡牌添加样式类
                zone.appendChild(img);
                // alert(`卡牌已放入区域 ${zoneId}`);
                //summonCard(location=zoneId, fileName)
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
            console.log(`区域 ${zoneId} 设置为攻击状态`);
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
            console.log(`区域 ${zoneId} 设置为防御状态`);
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
        if (JSON.stringify(result.data) !== JSON.stringify(lastData)) {
            console.log("Old data:", lastData); // Debug log
            lastData = result.data
            console.log("New data received:", result.data); // Debug log
            handleAction(result.data); // 将解构后的 data 传递给 handleAction
        } else {
            console.error("Invalid JSON format or Old message received:", result);
        }
    } catch (error) {
        console.error("Error fetching data:", error.message);
    }
}

// Function to handle different actions
function handleAction(data) {
    console.log("Received data in handleAction:", data); // Print the entire JSON data
    // const { action, location, card_id } = data;
    let { action, card_id, ...locations } = data;
    // Initialize location variables
    let location1 = null;
    const location0 = [];

    // Extract locations
    Object.entries(locations).forEach(([key, value]) => {
        if (key.startsWith("location_")) {
            const number = parseInt(key.split("_")[1], 10); // Extract the number part
            if (value === 1) {
                location1 = number; // Assign to location1
            } else if (value === 0) {
                location0.push(number); // Add to location0 array
            }
        }
    });


    console.log(`location1=${location1}`);
    console.log(`location0=[${location0.join(", ")}]`);
    console.log(action);
    // Handle action
    switch (action) { // Normalize action format
        case "normal_summon":
            normal_summon(location1, card_id); // Use location1 for "Normal Summon"
            break;

        case "tribute_summon":
            tribute_summon(location1, location0, card_id)
            break

        case "attach":
            normal_summon(location1, card_id)
            break

        case "special_summon_in_attack_position":
            normal_summon(location1, card_id)
            break

        case "special_summon_in_defense_position":
            normal_summon(location1, card_id)
            console.log("finish summon")
            setDefenseState(location1)
            console.log("finish set")
            break

        case "xyz_summon_in_attack_position":
            normal_summon(location1, card_id)
            break

        case "xyz_summon_in_defense_postion":
            normal_summon(location1, card_id)
            setDefenseState(location1)
            break


        case "link_summon":
            tribute_summon(location1, location0, card_id)
            break

        case "synchro_summon_in_attack_position":
            tribute_summon(location1, location0, card_id)
            break

        case "synchro_summon_in_defense_position":
            tribute_summon(location1, location0, card_id)
            setDefenseState(location1)
            break

        case "set":
            if((location1 >= 16 && location1 <= 20) || location1 == 8){
                normal_summon(location1, card_id=1)
                
            }
                
            else{
                normal_summon(location1, card_id=1)
                setDefenseState(location1)
            }
                
            break

        case "flip_summon":
            normal_summon(location1, card_id)
            break

        case "reverse":
            normal_summon(location1, card_id)
            break

        case "discard":
            location0.forEach(loc => deleteCard(loc, card_id))// Use all location0 values for "Discard"
            break

        case "banish":
            location0.forEach(loc => banish(loc))
            break

        case "destroy":
            location0.forEach(loc => deleteCard(loc, card_id))
            break

        case "return_to_hand":
            location0.forEach(loc => banish(loc))
            break

        case "return_to_deck":
            location0.forEach(loc => banish(loc))
            break

        case "mill":

            break

        case "activate":
            normal_summon(location1, card_id)
            break

        case "change_to_attack_position":
            setAttackState(location1)
            break

        case "change_to_defense_position":
            setDefenseState(location1)
            break

        case "send_to":
            tribute_summon(location1, location0, card_id)
            break

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

function normal_summon(location, card_id) {
    const zones = document.querySelectorAll('.zone'); // 获取所有区域
    const targetZone = zones[location - 1]; // 获取指定区域（1-based index）

    if (targetZone) {
        clearCardInZone(targetZone); // 仅移除旧卡牌

        // 添加新卡牌
        const card = document.createElement('img');
        card.src = `/data/card/${card_id}.jpg`; // 假设卡牌图片路径
        card.alt = `Card ${card_id}`;
        card.className = 'img'; // 为新卡牌添加样式类

        targetZone.appendChild(card); // 将新卡牌插入到区域
    } else {
        console.error(`Invalid location: ${location}`);
    }
    console.log("finish summon")
}

function tribute_summon(location1, location0, card_id){
    // Perform normal summon
    normal_summon(location1, card_id);

    // Loop through location0 array and delete cards
    for (const loc of location0) {
        deleteCard(loc);
    }
}

function banish(location){
    const zones = document.querySelectorAll('.zone'); // 获取所有区域
    const targetZone = zones[location - 1]; // 获取指定区域（1-based index）

    if (targetZone) {
        clearCardInZone(targetZone); // 仅移除旧卡牌
    } else {
        console.error(`Invalid location: ${location}`);
    }
}



const graveyardCards = []; // 用于存储墓地卡牌的正面路径

function deleteCard(location) {

    const zones = document.querySelectorAll('.zone'); // 获取所有区域
    const targetZone = zones[location - 1]; // 获取指定区域（1-based index）
    const graveyard = document.querySelector('.graveyard'); // 获取墓地区域

    if (!graveyard) {
        console.error("Graveyard zone not found.");
        return;
    }
    if (targetZone) {
        const card = targetZone.querySelector('.img'); // 查找卡牌元素
        
        const cardFront = card.src; // 获取卡牌正面图片路径
        graveyardCards.push(cardFront); // 将正面图片路径添加到墓地数组
        targetZone.removeChild(card); // 从当前区域移除卡牌

        // 墓地中显示统一的背面图片
        //graveyard.innerHTML = ''; // 可选：根据需求清空墓地区域
        const graveCard = document.createElement('img');
        graveCard.src = '/data/card/1.jpg'; // 假设背面显示 1.jpg
        graveCard.alt = 'Graveyard Card';
        graveCard.className = 'card grave-card'; // 添加类名
        graveyard.appendChild(graveCard);

        console.log(`Card discarded from location ${location} and moved to Graveyard.`);
        
    } else {
        console.error(`Invalid location: ${location}`);
    }
}




// Automatically refresh data every 2 seconds
setInterval(fetchLatestData, 1000);

// Fetch data immediately after the page loads
document.addEventListener('DOMContentLoaded', fetchLatestData);
