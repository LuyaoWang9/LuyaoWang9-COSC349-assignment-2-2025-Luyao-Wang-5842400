class NotebookApp {
    constructor() {
        this.notes = [];
        this.currentNote = null;
        this.stats = null;
        
        // API configuration
        this.apiBaseUrl = ''; // Remove /api prefix
        
        this.initializeEventListeners();
        this.loadNotes();
        this.loadStatistics();
        
        // Make app globally accessible for button onclick events
        window.app = this;
    }

    initializeEventListeners() {
        document.getElementById('newNoteBtn').addEventListener('click', () => this.createNewNote());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveNote());
        document.getElementById('deleteBtn').addEventListener('click', () => this.deleteNote());
        document.getElementById('refreshStatsBtn').addEventListener('click', () => this.loadStatistics());
        document.getElementById('refreshNotesBtn').addEventListener('click', () => this.loadNotes());
        document.getElementById('lambdaStatsBtn').addEventListener('click', () => this.loadLambdaStatistics());
        document.getElementById('uploadBtn').addEventListener('click', () => this.triggerFileUpload());
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileUpload(e));
        document.getElementById('backupBtn').addEventListener('click', () => this.backupNote());
        
        // Auto-save on content change (with debouncing)
        let saveTimeout;
        const autoSave = () => {
            clearTimeout(saveTimeout);
            if (this.currentNote) {
                saveTimeout = setTimeout(() => this.saveNote(), 1000);
            }
        };
        
        document.getElementById('noteTitle').addEventListener('input', autoSave);
        document.getElementById('noteContent').addEventListener('input', autoSave);
    }

    async loadNotes() {
        try {
            const refreshBtn = document.getElementById('refreshNotesBtn');
            refreshBtn.classList.add('loading');
            
            const response = await fetch(`${this.apiBaseUrl}/notes`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.notes = await response.json();
            this.renderNotesList();
            
        } catch (error) {
            console.error('Error loading notes:', error);
            alert('Failed to load notes. Please check if the backend is running.');
        } finally {
            const refreshBtn = document.getElementById('refreshNotesBtn');
            refreshBtn.classList.remove('loading');
        }
    }

    async loadStatistics() {
        try {
            const refreshBtn = document.getElementById('refreshStatsBtn');
            refreshBtn.classList.add('loading');
            
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.stats = {
                total_notes: data.total_notes,
                notes_today: data.recent_notes_24h,
                total_characters: 0,
                average_length: 0,
                last_updated: new Date().toISOString(),
                source: 'RDS MySQL'
            };
            
            this.calculateCharacterStats();
            this.renderStatistics();
            
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.calculateLocalStatistics();
        } finally {
            const refreshBtn = document.getElementById('refreshStatsBtn');
            refreshBtn.classList.remove('loading');
        }
    }

    async loadLambdaStatistics() {
        try {
            const lambdaBtn = document.getElementById('lambdaStatsBtn');
            lambdaBtn.classList.add('loading');
            lambdaBtn.textContent = 'Loading...';
            
            console.log('🔄 Fetching Lambda statistics...');
            const response = await fetch(`${this.apiBaseUrl}/lambda-stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Lambda stats response:', data);
            
            if (data.error) {
                throw new Error(`Backend error: ${data.error}`);
            }
            
            if (data.lambda_response && data.lambda_response.body) {
                const lambdaStats = JSON.parse(data.lambda_response.body);
                console.log('📊 Lambda statistics:', lambdaStats);
                
                this.stats = {
                    total_notes: lambdaStats.total_notes,
                    notes_today: lambdaStats.notes_today,
                    total_characters: lambdaStats.total_characters,
                    average_length: lambdaStats.average_length,
                    last_updated: lambdaStats.last_updated,
                    source: 'AWS Lambda'
                };
                this.renderStatistics();
                
                alert('✅ Lambda statistics loaded successfully!');
            } else {
                throw new Error('Invalid Lambda response format');
            }
            
        } catch (error) {
            console.error('❌ Error loading Lambda statistics:', error);
            alert(`Failed to load Lambda statistics:\n${error.message}\n\nCheck browser console for details.`);
            this.calculateLocalStatistics();
        } finally {
            const lambdaBtn = document.getElementById('lambdaStatsBtn');
            lambdaBtn.classList.remove('loading');
            lambdaBtn.textContent = 'λ Lambda Stats';
        }
    }

    calculateCharacterStats() {
        if (this.notes.length > 0) {
            const totalChars = this.notes.reduce((sum, note) => sum + (note.content?.length || 0), 0);
            const avgLength = totalChars / this.notes.length;
            
            this.stats.total_characters = totalChars;
            this.stats.average_length = parseFloat(avgLength.toFixed(2));
        }
    }

    calculateLocalStatistics() {
        const totalNotes = this.notes.length;
        const today = new Date().toISOString().split('T')[0];
        const notesToday = this.notes.filter(note => {
            const noteDate = new Date(note.updated_at).toISOString().split('T')[0];
            return noteDate === today;
        }).length;
        
        const totalChars = this.notes.reduce((sum, note) => sum + (note.content?.length || 0), 0);
        const avgLength = totalNotes > 0 ? (totalChars / totalNotes).toFixed(2) : 0;
        
        this.stats = {
            total_notes: totalNotes,
            notes_today: notesToday,
            total_characters: totalChars,
            average_length: parseFloat(avgLength),
            last_updated: new Date().toISOString(),
            source: 'Local Calculation'
        };
        
        this.renderStatistics();
    }

    renderStatistics() {
        if (!this.stats) return;
        
        document.getElementById('totalNotes').textContent = this.stats.total_notes.toLocaleString();
        document.getElementById('notesToday').textContent = this.stats.notes_today.toLocaleString();
        document.getElementById('totalChars').textContent = this.stats.total_characters.toLocaleString();
        document.getElementById('avgLength').textContent = this.stats.average_length.toFixed(1);
        
        const lastUpdated = document.getElementById('lastUpdated');
        if (this.stats.last_updated) {
            const date = new Date(this.stats.last_updated);
            lastUpdated.textContent = `Last updated: ${date.toLocaleString()}`;
        }
        
        const dataSource = document.getElementById('dataSource');
        dataSource.textContent = this.stats.source;
        dataSource.className = 'data-source';
        
        if (this.stats.source === 'AWS Lambda') {
            dataSource.classList.add('lambda');
        } else if (this.stats.source === 'RDS MySQL') {
            dataSource.classList.add('rds');
        } else {
            dataSource.classList.add('local');
        }
    }

    renderNotesList() {
        const notesList = document.getElementById('notesList');
        notesList.innerHTML = '';

        if (this.notes.length === 0) {
            notesList.innerHTML = '<p class="empty-notes">No notes yet. Create your first note!</p>';
            return;
        }

        this.notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = 'note-item';
            if (this.currentNote && this.currentNote.id === note.id) {
                noteElement.classList.add('active');
            }
            
            const preview = note.content ? 
                note.content.substring(0, 100) + (note.content.length > 100 ? '...' : '') : 
                'No content';
                
            const date = new Date(note.updated_at).toLocaleDateString();
            
            noteElement.innerHTML = `
                <div class="note-title">${this.escapeHtml(note.title) || 'Untitled'}</div>
                <div class="note-preview">${this.escapeHtml(preview)}</div>
                <div class="note-date">${date}</div>
            `;
            
            noteElement.addEventListener('click', () => this.selectNote(note));
            notesList.appendChild(noteElement);
        });
    }

    selectNote(note) {
        this.currentNote = note;
        this.renderNotesList();
        this.showEditor();
        
        document.getElementById('noteTitle').value = note.title || '';
        document.getElementById('noteContent').value = note.content || '';
        
        this.loadAttachments();
        document.getElementById('attachmentsSection').style.display = 'block';
    }

    createNewNote() {
        this.currentNote = { id: null, title: '', content: '' };
        this.renderNotesList();
        this.showEditor();
        
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        document.getElementById('attachmentsSection').style.display = 'none';
        document.getElementById('noteTitle').focus();
    }

    showEditor() {
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('noteEditor').style.display = 'flex';
    }

    hideEditor() {
        document.getElementById('emptyState').style.display = 'flex';
        document.getElementById('noteEditor').style.display = 'none';
        this.currentNote = null;
        this.renderNotesList();
    }

    async saveNote() {
        const title = document.getElementById('noteTitle').value;
        const content = document.getElementById('noteContent').value;

        if (!title.trim() && !content.trim()) {
            return;
        }

        try {
            if (this.currentNote.id) {
                const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            } else {
                const response = await fetch(`${this.apiBaseUrl}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                this.currentNote.id = result.id;
            }
            
            await this.loadNotes();
            this.loadStatistics();
            
        } catch (error) {
            console.error('Error saving note:', error);
            alert('Failed to save note. Please try again.');
        }
    }

    async deleteNote() {
        if (!this.currentNote?.id) return;

        if (confirm('Are you sure you want to delete this note?')) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                this.currentNote = null;
                this.hideEditor();
                await this.loadNotes();
                this.loadStatistics();
            } catch (error) {
                console.error('Error deleting note:', error);
                alert('Failed to delete note.');
            }
        }
    }

    async loadAttachments() {
        if (!this.currentNote?.id) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}/attachments`);
            if (!response.ok) throw new Error('Failed to load attachments');
            
            const data = await response.json();
            this.renderAttachments(data.attachments);
        } catch (error) {
            console.error('Error loading attachments:', error);
        }
    }

    renderAttachments(attachments) {
        const attachmentsList = document.getElementById('attachmentsList');
        
        if (!attachments || attachments.length === 0) {
            attachmentsList.innerHTML = '<p class="empty-attachments">No attachments</p>';
            return;
        }
        
        attachmentsList.innerHTML = attachments.map(attachment => `
            <div class="attachment-item">
                <div class="attachment-info">
                    <span class="attachment-filename">${this.escapeHtml(attachment.filename)}</span>
                    <span class="attachment-size">${this.formatFileSize(attachment.size)}</span>
                </div>
                <div class="attachment-actions">
                    <button class="btn-small btn-primary" onclick="app.downloadAttachment('${attachment.key}')">
                        📥 Download
                    </button>
                    <button class="btn-small btn-danger" onclick="app.deleteAttachment('${attachment.key}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    triggerFileUpload() {
        document.getElementById('fileInput').click();
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file || !this.currentNote?.id) return;
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}/attachments`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Upload failed');
            
            const result = await response.json();
            console.log('File uploaded:', result);
            
            await this.loadAttachments();
            event.target.value = '';
            
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Failed to upload file');
        }
    }

    async downloadAttachment(s3Key) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/attachments/${encodeURIComponent(s3Key)}`);
            if (!response.ok) throw new Error('Failed to get download URL');
            
            const data = await response.json();
            window.open(data.download_url, '_blank');
            
        } catch (error) {
            console.error('Error downloading attachment:', error);
            alert('Failed to download file');
        }
    }

    async deleteAttachment(s3Key) {
        if (!confirm('Are you sure you want to delete this attachment?')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/attachments/${encodeURIComponent(s3Key)}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Delete failed');
            
            await this.loadAttachments();
            
        } catch (error) {
            console.error('Error deleting attachment:', error);
            alert('Failed to delete file');
        }
    }

    async backupNote() {
        if (!this.currentNote?.id) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}/backup`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Backup failed');
            
            const result = await response.json();
            alert('✅ Note backed up successfully to S3!');
            
        } catch (error) {
            console.error('Error backing up note:', error);
            alert('Failed to backup note');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new NotebookApp();
});