// ============================================
// משתנים גלובליים
// ============================================
let bibleContent = null;
let parsedBibleData = null;
let logInterval = null;

// ============================================
// אתחול
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    loadProjects();
    loadBudget();
    
    const fileInput = document.getElementById('bibleFile');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    bibleContent = event.target.result;
                    document.getElementById('biblePreview').style.display = 'block';
                    document.getElementById('biblePreview').querySelector('span').textContent = '📄 ' + file.name;
                    log('📄 בייבל נטען: ' + file.name + ' (' + bibleContent.length + ' תווים)');
                    parseBibleAndShowFields(bibleContent);
                };
                reader.readAsText(file);
            }
        });
    }
    
    const form = document.getElementById('createForm');
    if (form) {
        form.addEventListener('submit', createProject);
    }
});

// ============================================
// חישוב מילים לפרק
// ============================================
function calculateWordsPerChapter() {
    // ===== קח את המילים לפרק ישירות =====
    const minPerChapter = parseInt(document.getElementById('minWords').value) || 1000;
    const maxPerChapter = parseInt(document.getElementById('maxWords').value) || 1200;
    const avgPerChapter = Math.round((minPerChapter + maxPerChapter) / 2);
    
    // ===== עדכן את הממוצע המוצג =====
    document.getElementById('extractedWordsPerChapter').value = avgPerChapter;
    
    // ===== עדכן את טווח הספר לפי זה =====
    const chapterCount = parseInt(document.getElementById('extractedChapterCount').value) || 5;
    document.getElementById('extractedMinWords').value = minPerChapter * chapterCount;
    document.getElementById('extractedMaxWords').value = maxPerChapter * chapterCount;
}
// ============================================
// ניתוח בייבל
// ============================================
async function parseBibleAndShowFields(bibleText) {
    try {
        log('🔍 מנתח בייבל...');
        const response = await fetch('/api/bible/parse', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ bible_content: bibleText })
        });
        
        if (!response.ok) throw new Error('Failed to parse');
        
        const data = await response.json();
        parsedBibleData = data;
        
        document.getElementById('extractedTitle').value = data.title || '';
        document.getElementById('extractedType').value = data.book_type || 'novel';
        
        // ===== שמירת הנתונים מהבייבל =====
        const totalMin = data.min_words || 3000;
        const totalMax = data.max_words || 5000;
        const chapterCount = data.chapter_count || 5;
        
        document.getElementById('extractedMinWords').value = totalMin;
        document.getElementById('extractedMaxWords').value = totalMax;
        document.getElementById('extractedChapterCount').value = chapterCount;
        
        document.getElementById('extractedPOV').value = data.pov || '';
        document.getElementById('extractedTense').value = data.tense || '';
        document.getElementById('extractedTone').value = data.tone || '';
        document.getElementById('extractedCharacters').value = (data.characters || []).join(', ');
        document.getElementById('extractedSetting').value = data.setting || '';
        document.getElementById('extractedCorePromise').value = data.core_promise || '';
        document.getElementById('extractedPitch').value = data.one_sentence_pitch || '';
        
        // ===== עדכן את minWords ו-maxWords (מילים לפרק) לפי הבייבל =====
        const minPerChapter = Math.round(totalMin / chapterCount);
        const maxPerChapter = Math.round(totalMax / chapterCount);
        document.getElementById('minWords').value = minPerChapter || 1000;
        document.getElementById('maxWords').value = maxPerChapter || 1200;
        
        // ===== חשב את הממוצע המוצג =====
        calculateWordsPerChapter();
        
        document.getElementById('bibleFields').classList.add('show');
        
        log('✅ בייבל נ przeanalizowany: ' + data.title + ' (' + data.chapter_count + ' פרקים, ' + data.min_words + '-' + data.max_words + ' מילים)');
    } catch (err) {
        log('❌ שגיאה בניתוח בייבל: ' + err.message);
        alert('❌ שגיאה בניתוח הבייבל: ' + err.message);
    }
}

// ============================================
// מילוי הפרויקט מהבייבל
// ============================================
function fillProjectFromBible() {
    document.getElementById('projectName').value = document.getElementById('extractedTitle').value;
    document.getElementById('bookType').value = document.getElementById('extractedType').value;
    
    // ===== minWords ו-maxWords כבר מעודכנים על ידי calculateWordsPerChapter =====
    document.getElementById('goal').value = document.getElementById('extractedPitch').value;
    
    log('✅ הנתונים הועברו לשדות הראשיים');
    document.querySelector('.card').scrollIntoView({ behavior: 'smooth' });
}
// ============================================
// הסרת בייבל
// ============================================
function removeBible() {
    bibleContent = null;
    parsedBibleData = null;
    document.getElementById('biblePreview').style.display = 'none';
    document.getElementById('bibleFields').classList.remove('show');
    document.getElementById('bibleFile').value = '';
    log('🗑️ בייבל הוסר');
}

// ============================================
// יצירת פרויקט
// ============================================
async function createProject(e) {
    e.preventDefault();
    
    const name = document.getElementById('projectName').value;
    const bookType = document.getElementById('bookType').value;
    const goal = document.getElementById('goal').value;
    const minWords = parseInt(document.getElementById('minWords').value) || 300;
    const maxWords = parseInt(document.getElementById('maxWords').value) || 500;
    
    const targetMinWords = parseInt(document.getElementById('extractedMinWords').value) || 3000;
    const targetMaxWords = parseInt(document.getElementById('extractedMaxWords').value) || 5000;
    const chapterCount = parseInt(document.getElementById('extractedChapterCount').value) || 5;
    const wordsPerChapter = parseInt(document.getElementById('extractedWordsPerChapter').value) || 1000;
    
    if (!name) {
        alert('❌ יש להזין שם פרויקט');
        return;
    }
    
    if (!bibleContent) {
        alert('❌ יש להעלות בייבל!');
        return;
    }
    
const data = {
    name: name,
    book_type: bookType,
    goal: goal,
    min_words: minWords,  // זה minWords (1000)
    max_words: maxWords,  // זה maxWords (1200)
    bible_content: bibleContent,
    target_total_words_min: targetMinWords,
    target_total_words_max: targetMaxWords,
    target_chapter_count: chapterCount,
    target_words_per_chapter: Math.round((minWords + maxWords) / 2)  // הממוצע שנשלח לפייפליין
};    
    log('📤 יוצר פרויקט: ' + name + ' (' + chapterCount + ' פרקים, ' + targetMinWords + '-' + targetMaxWords + ' מילים)');
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create');
        }
        
        const result = await response.json();
        log('✅ פרויקט נוצר: ' + result.name);
        
        document.getElementById('createForm').reset();
        bibleContent = null;
        parsedBibleData = null;
        document.getElementById('biblePreview').style.display = 'none';
        document.getElementById('bibleFields').classList.remove('show');
        loadProjects();
    } catch (err) {
        log('❌ שגיאה ביצירה: ' + err.message);
        alert('❌ שגיאה: ' + err.message);
    }
}

// ============================================
// רשימת פרויקטים
// ============================================
async function loadProjects() {
    log('🔄 טוען רשימת פרויקטים...');
    try {
        const response = await fetch('/api/projects');
        if (!response.ok) throw new Error('Failed to load');
        const data = await response.json();
        renderProjects(data.projects || []);
    } catch (err) {
        document.getElementById('projectsList').innerHTML = '<div style="color: #ff4444;">❌ שגיאה בטעינה: ' + err.message + '</div>';
        log('❌ שגיאה בטעינת פרויקטים: ' + err.message);
    }
}

function renderProjects(projects) {
    const container = document.getElementById('projectsList');
    if (!projects || projects.length === 0) {
        container.innerHTML = '<div style="color: #666; text-align: center; padding: 20px;">אין פרויקטים. צור אחד חדש!</div>';
        return;
    }
    
    let html = '<ul class="project-list">';
    projects.forEach(p => {
        const statusClass = 'status-' + p.state;
        const statusLabel = p.state === 'draft' ? 'טיוטה' : 
                           p.state === 'active' ? '🏃 בכתיבה' : 
                           p.state === 'completed' ? '✅ הושלם' : 
                           p.state === 'failed' ? '❌ נכשל' : p.state;
        
        html += `
            <li class="project-item">
                <div class="project-info">
                    <div class="project-name">${p.name}</div>
                    <div class="project-meta">
                        <span class="status-badge ${statusClass}">${statusLabel}</span>
                        ${p.book_type || 'novel'} • ${p.created_at ? new Date(p.created_at).toLocaleDateString('he-IL') : ''}
                    </div>
                </div>
                <div class="project-actions">
                    <button class="btn btn-sm btn-success" onclick="runProject('${p.id}')">▶️ הפעל</button>
                    <button class="btn btn-sm btn-primary" onclick="viewProject('${p.id}')">📄 צפה</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProject('${p.id}')">🗑️</button>
                    ${p.state === 'completed' ? `
                        <button class="btn btn-sm btn-warning" onclick="exportBook('${p.id}', 'docx')">📤 DOCX</button>
                        <button class="btn btn-sm btn-warning" onclick="exportBook('${p.id}', 'epub')">📤 EPUB</button>
                    ` : ''}
                </div>
            </li>
        `;
    });
    html += '</ul>';
    container.innerHTML = html;
}

// ============================================
// הפעלת פרויקט
// ============================================
async function runProject(projectId) {
    log('▶️ מפעיל הפקה לפרויקט: ' + projectId);
    try {
        const response = await fetch('/api/projects/' + projectId + '/run', {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Unknown error');
        }
        const result = await response.json();
        if (result.error) {
            log('❌ ' + result.error);
            alert('❌ ' + result.error);
        } else {
            log('✅ הפקה הופעלה: ' + (result.message || 'success'));
            loadProjects();
            startStatusPolling(projectId);
        }
    } catch (err) {
        log('❌ שגיאה בהפעלה: ' + err.message);
        alert('❌ שגיאה: ' + err.message);
    }
}

// ============================================
// צפייה בפרויקט
// ============================================
async function viewProject(projectId) {
    log('📄 טוען תוכן פרויקט: ' + projectId);
    try {
        const response = await fetch('/api/projects/' + projectId);
        if (!response.ok) throw new Error('Failed to load');
        const project = await response.json();
        
        const response2 = await fetch('/api/projects/' + projectId + '/manuscript');
        if (!response2.ok) throw new Error('Failed to load manuscript');
        const data = await response2.json();
        
        document.getElementById('viewTitle').textContent = '📄 ' + project.name;
        document.getElementById('viewCard').classList.remove('hidden');
        document.getElementById('viewContent').textContent = 
            '📊 סטטוס: ' + project.state + '\n' +
            '📖 סוג: ' + project.book_type + '\n' +
            '📝 מילים: ' + (data.word_count || 0) + '\n' +
            '📌 פרק נוכחי: ' + (project.current_chapter || 0) + '\n' +
            '─────────────────────\n\n' +
            (data.content || 'טרם נכתב תוכן') + 
            (data.content && data.content.length >= 10000 ? '\n\n... (קטע ראשון מתוך הספר)' : '');
        
        log('📄 תוכן נטען, ' + (data.word_count || 0) + ' מילים');
    } catch (err) {
        log('❌ שגיאה בטעינת תוכן: ' + err.message);
        alert('❌ שגיאה: ' + err.message);
    }
}

function closeView() {
    document.getElementById('viewCard').classList.add('hidden');
}

// ============================================
// מחיקת פרויקט
// ============================================
async function deleteProject(projectId) {
    if (!confirm('האם למחוק פרויקט זה?')) return;
    log('🗑️ מוחק פרויקט: ' + projectId);
    try {
        const response = await fetch('/api/projects/' + projectId, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete');
        log('✅ פרויקט נמחק');
        loadProjects();
    } catch (err) {
        log('❌ שגיאה במחיקה: ' + err.message);
        alert('❌ שגיאה: ' + err.message);
    }
}

// ============================================
// ייצוא
// ============================================
async function exportBook(projectId, format) {
    log('📤 מייצא ' + format + ' לפרויקט: ' + projectId);
    try {
        const response = await fetch('/api/projects/' + projectId + '/export', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ format: format })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Export failed');
        }
        const result = await response.json();
        log('✅ ' + result.message);
    } catch (err) {
        log('❌ שגיאה בייצוא: ' + err.message);
        alert('❌ שגיאה: ' + err.message);
    }
}

// ============================================
// תקציב
// ============================================
async function loadBudget() {
    try {
        const response = await fetch('/api/budget');
        if (!response.ok) throw new Error('Failed');
        const data = await response.json();
        if (data.error) {
            document.getElementById('budgetDisplay').textContent = '❌';
            document.getElementById('budgetStatus').textContent = data.error;
        } else {
            const used = data.used || 0;
            const limit = data.limit || 2.0;
            document.getElementById('budgetDisplay').textContent = '$' + used.toFixed(2);
            document.getElementById('budgetStatus').textContent = 'תקציב: $' + limit.toFixed(2);
        }
    } catch (err) {
        document.getElementById('budgetDisplay').textContent = '❌';
        document.getElementById('budgetStatus').textContent = err.message;
    }
}
async function checkBalance() {
    const resultDiv = document.getElementById('balanceResult');
    resultDiv.textContent = '🔄 בודק...';
    try {
        const response = await fetch('/api/balance');
        const data = await response.json();
        if (data.error) {
            resultDiv.textContent = '❌ ' + data.error;
        } else {
            resultDiv.innerHTML = 
                '💰 יתרה: <strong>' + data.total_balance + '</strong> ' + data.currency + 
                ' | טעון: ' + data.topped_up + 
                ' | מענק: ' + data.granted + 
                ' | ' + data.status;
        }
    } catch (err) {
        resultDiv.textContent = '❌ שגיאה: ' + err.message;
    }
}

// ============================================
// סטטוס פולסינג
// ============================================
function startStatusPolling(projectId) {
    if (logInterval) clearInterval(logInterval);
    logInterval = setInterval(async function() {
        try {
            const response = await fetch('/api/projects/' + projectId + '/status');
            if (!response.ok) throw new Error('Failed');
            const data = await response.json();
            
            if (data.state === 'completed') {
                clearInterval(logInterval);
                logInterval = null;
                log('📌 פרויקט הסתיים: ' + data.state);
                loadProjects();
                // ===== פופאפ סיום =====
                alert('✅ הספר הושלם! (' + data.total_words + ' מילים)');
            } else if (data.state === 'failed') {
                clearInterval(logInterval);
                logInterval = null;
                log('❌ פרויקט נכשל');
                loadProjects();
                alert('❌ הכתיבה נכשלה. בדוק את הלוג.');
            } else if (data.state === 'active') {
                const chapterDisplay = data.current_chapter || 0;
                const displayChapter = chapterDisplay > 0 ? chapterDisplay : '1';
                log('⏳ בכתיבה... פרק ' + displayChapter + ' (' + (data.total_words || 0) + ' מילים)');
            }
        } catch (err) {
            // silent
        }
    }, 3000);
}

// ============================================
// לוג
// ============================================
function log(message) {
    const area = document.getElementById('logArea');
    const time = new Date().toLocaleTimeString('he-IL');
    area.innerHTML += '\n[' + time + '] ' + message;
    area.scrollTop = area.scrollHeight;
}