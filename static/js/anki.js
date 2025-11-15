// Обработка переключения между методами ввода
const radioButtons = document.querySelectorAll('input[name="input_method"]');
const textFields = document.getElementById("textFields");
const fileFields = document.getElementById("fileFields");
const fieldsContainer = document.getElementById("fieldsContainer");

function toggleInputFields() {
  const selectedValue = document.querySelector(
    'input[name="input_method"]:checked'
  ).value;

  // Показываем контейнер полей
  fieldsContainer.classList.add("active");

  // Переключаем видимость полей
  if (selectedValue === "text") {
    textFields.classList.add("active");
    fileFields.classList.remove("active");
    hideError(); // Скрываем ошибки при переключении
  } else {
    textFields.classList.remove("active");
    fileFields.classList.add("active");
    hideError(); // Скрываем ошибки при переключении
  }
}

// Добавляем обработчики событий
radioButtons.forEach((radio) => {
  radio.addEventListener("change", toggleInputFields);
});

// Инициализация при загрузке страницы
toggleInputFields();

// Функции проверки ввода
function validateTextInput() {
  const englishText = document.getElementById("englishText").value;
  const russianText = document.getElementById("russianText").value;

  const englishLines = englishText
    .split("\n")
    .filter((line) => line.trim() !== "");
  const russianLines = russianText
    .split("\n")
    .filter((line) => line.trim() !== "");

  if (englishLines.length === 0 && russianLines.length === 0) {
    return { isValid: true, message: "" };
  }

  if (englishLines.length !== russianLines.length) {
    return {
      isValid: false,
      message: `Количество строк не совпадает! Английских: ${englishLines.length}, Русских: ${russianLines.length}`,
    };
  }

  return { isValid: true, message: "" };
}

function validateFileInput() {
  const englishFile = document.getElementById("englishFile").files[0];
  const russianFile = document.getElementById("russianFile").files[0];

  if (!englishFile || !russianFile) {
    return { isValid: false, message: "Пожалуйста, выберите оба файла" };
  }

  // Проверяем расширения файлов
  const validExtensions = [".txt", ".csv"];
  const engExt = "." + englishFile.name.split(".").pop().toLowerCase();
  const rusExt = "." + russianFile.name.split(".").pop().toLowerCase();

  if (!validExtensions.includes(engExt) || !validExtensions.includes(rusExt)) {
    return {
      isValid: false,
      message: "Поддерживаются только файлы .txt и .csv",
    };
  }

  return { isValid: true, message: "" };
}

// Функция для чтения файла и подсчета строк
function countLinesInFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = function (e) {
      const content = e.target.result;
      const lines = content.split("\n").filter((line) => line.trim() !== "");
      resolve(lines.length);
    };

    reader.onerror = function () {
      reject(new Error("Ошибка чтения файла"));
    };

    reader.readAsText(file);
  });
}

// Проверка файлов при их выборе
async function validateFilesLineCount() {
  const englishFile = document.getElementById("englishFile").files[0];
  const russianFile = document.getElementById("russianFile").files[0];

  if (!englishFile || !russianFile) {
    return { isValid: false, message: "Выберите оба файла" };
  }

  try {
    const engLineCount = await countLinesInFile(englishFile);
    const rusLineCount = await countLinesInFile(russianFile);

    if (engLineCount !== rusLineCount) {
      return {
        isValid: false,
        message: `Количество строк в файлах не совпадает! Английский: ${engLineCount}, Русский: ${rusLineCount}`,
      };
    }

    return { isValid: true, message: "" };
  } catch (error) {
    return { isValid: false, message: "Ошибка при чтении файлов" };
  }
}

// Функция для отображения ошибок
function showError(message) {
  const notification = document.createElement("div");
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #ff6b6b;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  `;

  notification.textContent = message;
  document.body.appendChild(notification);

  // Автоматически удаляем через 3 секунды
  setTimeout(() => {
    document.body.removeChild(notification);
  }, 3000);
}

function hideError() {
  const errorDiv = document.getElementById("errorMessage");
  if (errorDiv) {
    errorDiv.style.display = "none";
  }
}

// Обработчики событий для реальной проверки
function setupValidation() {
  // Проверка текстовых полей при вводе
  const englishTextarea = document.getElementById("englishText");
  const russianTextarea = document.getElementById("russianText");

  if (englishTextarea && russianTextarea) {
    englishTextarea.addEventListener("input", validateTextInputRealTime);
    russianTextarea.addEventListener("input", validateTextInputRealTime);
  }

  // Проверка файлов при выборе
  const englishFileInput = document.getElementById("englishFile");
  const russianFileInput = document.getElementById("russianFile");

  if (englishFileInput && russianFileInput) {
    englishFileInput.addEventListener("change", validateFilesRealTime);
    russianFileInput.addEventListener("change", validateFilesRealTime);
  }
}

// Реалтайм проверка текстовых полей
function validateTextInputRealTime() {
  const selectedMethod = document.querySelector(
    'input[name="input_method"]:checked'
  ).value;

  if (selectedMethod === "text") {
    const result = validateTextInput();
    if (!result.isValid) {
      showError(result.message);
    } else {
      hideError();
    }
  }
}

// Реалтайм проверка файлов
async function validateFilesRealTime() {
  const selectedMethod = document.querySelector(
    'input[name="input_method"]:checked'
  ).value;

  if (selectedMethod === "file") {
    const englishFile = document.getElementById("englishFile").files[0];
    const russianFile = document.getElementById("russianFile").files[0];

    if (englishFile && russianFile) {
      const result = await validateFilesLineCount();
      if (!result.isValid) {
        showError(result.message);
      } else {
        hideError();
      }
    }
  }
}

// Упрощенная версия функции обработки кнопки "Создать"
async function handleCreateDeck() {
  const selectedMethod = document.querySelector(
    'input[name="input_method"]:checked'
  ).value;

  let validationResult;

  if (selectedMethod === "text") {
    validationResult = validateTextInput();
  } else {
    validationResult = await validateFilesLineCount();
  }

  if (!validationResult.isValid) {
    showError(validationResult.message);
    return;
  }

  const createButton = document.getElementById("createButton");
  const originalText = createButton.textContent;
  createButton.textContent = "Создание...";
  createButton.disabled = true;

  try {
    const formData = new FormData();
    formData.append("input_method", selectedMethod);
    formData.append("deck_name", document.getElementById("deck_name").value);

    if (selectedMethod === "text") {
      formData.append(
        "english_text",
        document.getElementById("englishText").value
      );
      formData.append(
        "russian_text",
        document.getElementById("russianText").value
      );
    } else {
      formData.append(
        "english_file",
        document.getElementById("englishFile").files[0]
      );
      formData.append(
        "russian_file",
        document.getElementById("russianFile").files[0]
      );
    }

    const response = await fetch("/generate_deck", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Ошибка сервера");
    }

    // Скачиваем файл
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = document.getElementById("deck_name").value + ".apkg";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showSuccess("Колода успешно создана и скачана!");
  } catch (error) {
    showError("Ошибка: " + error.message);
  } finally {
    createButton.textContent = originalText;
    createButton.disabled = false;
  }
}

// Функция для показа успешных уведомлений
function showSuccess(message) {
  const notification = document.createElement("div");
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #4ecdc4;
        color: white;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;

  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    document.body.removeChild(notification);
  }, 5000);
}
// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
  setupValidation();

  // Обновляем обработчик кнопки
  const createButton = document.getElementById("createButton");
  if (createButton) {
    createButton.addEventListener("click", handleCreateDeck);
  }
});
