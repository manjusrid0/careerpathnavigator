document.addEventListener('DOMContentLoaded', function() {

  // Helper
  const $ = id => document.getElementById(id);

  // Containers
  const eduList = $('education-list');
  const expList = $('experience-list');

  // --- Functions ---
  function updatePreview() {
    $('r-name').innerText = $('fullName').value || 'Your Name';
    $('r-title').innerText = $('title').value || 'Job Title';
    $('r-contact').innerText = [ $('email').value, $('phone').value, $('location').value ].filter(Boolean).join(' • ');
    $('r-summary').innerText = $('summary').value || '';

    // Skills
    const skillsList = $('r-skills').querySelector('.skills-list');
    skillsList.innerHTML = '';
    $('skills-input').value.split(',').map(s=>s.trim()).filter(Boolean).forEach(skill=>{
      const span = document.createElement('span');
      span.className = 'skill-chip';
      span.innerText = skill;
      skillsList.appendChild(span);
    });

    // Education
    const eduContainer = $('r-education');
    eduContainer.innerHTML = '<h4>Education</h4>';
    document.querySelectorAll('.edu-block').forEach(block => {
      const degree = block.querySelector('.edu-degree').value;
      const inst = block.querySelector('.edu-institution').value;
      const year = block.querySelector('.edu-year').value;
      if(degree || inst || year){
        const div = document.createElement('div');
        div.innerText = `${degree} — ${inst} ${year ? '• ' + year : ''}`;
        eduContainer.appendChild(div);
      }
    });

    // Experience
    const expContainer = $('r-experience');
    expContainer.innerHTML = '<h4>Experience</h4>';
    document.querySelectorAll('.exp-block').forEach(block => {
      const title = block.querySelector('.exp-title').value;
      const comp = block.querySelector('.exp-company').value;
      const dur = block.querySelector('.exp-duration').value;
      const desc = block.querySelector('.exp-desc').value;
      if(title || comp || dur || desc){
        const div = document.createElement('div');
        div.innerHTML = `<strong>${title} — ${comp} ${dur ? '• '+dur : ''}</strong><div>${desc}</div>`;
        expContainer.appendChild(div);
      }
    });
  }

  function addEducation() {
    const div = document.createElement('div');
    div.className = 'edu-block';
    div.innerHTML = `
      <input class="edu-degree" placeholder="Degree / Course"/>
      <input class="edu-institution" placeholder="Institution"/>
      <input class="edu-year" placeholder="Year"/>
      <button type="button" class="remove-btn">Remove</button>
    `;
    eduList.appendChild(div);
    div.querySelector('.remove-btn').addEventListener('click', () => { div.remove(); updatePreview(); });
    div.querySelectorAll('input').forEach(inp => inp.addEventListener('input', updatePreview));
  }

  function addExperience() {
    const div = document.createElement('div');
    div.className = 'exp-block';
    div.innerHTML = `
      <input class="exp-title" placeholder="Job Title"/>
      <input class="exp-company" placeholder="Company"/>
      <input class="exp-duration" placeholder="Duration"/>
      <textarea class="exp-desc" placeholder="Description"></textarea>
      <button type="button" class="remove-btn">Remove</button>
    `;
    expList.appendChild(div);
    div.querySelector('.remove-btn').addEventListener('click', () => { div.remove(); updatePreview(); });
    div.querySelectorAll('input, textarea').forEach(inp => inp.addEventListener('input', updatePreview));
  }

  function downloadJSON() {
    const data = {
      personal: {
        fullName: $('fullName').value,
        title: $('title').value,
        email: $('email').value,
        phone: $('phone').value,
        location: $('location').value,
        summary: $('summary').value
      },
      skills: $('skills-input').value.split(',').map(s=>s.trim()).filter(Boolean),
      education: Array.from(document.querySelectorAll('.edu-block')).map(b => ({
        degree: b.querySelector('.edu-degree').value,
        institution: b.querySelector('.edu-institution').value,
        year: b.querySelector('.edu-year').value
      })),
      experience: Array.from(document.querySelectorAll('.exp-block')).map(b => ({
        title: b.querySelector('.exp-title').value,
        company: b.querySelector('.exp-company').value,
        duration: b.querySelector('.exp-duration').value,
        description: b.querySelector('.exp-desc').value
      }))
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (data.personal.fullName || 'resume') + '.json';
    a.click();
  }

  async function exportPDF() {
    updatePreview();
    const { jsPDF } = window.jspdf;
    const preview = $('resume-preview');
    const canvas = await html2canvas(preview, {scale:2});
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({unit:'pt', format:'a4'});
    const pdfWidth = pdf.internal.pageSize.getWidth() - 40;
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    pdf.addImage(imgData,'PNG',20,20,pdfWidth,pdfHeight);
    pdf.save(($('fullName').value || 'resume')+'.pdf');
  }

  function clearAll() {
    $('resume-form').reset();
    eduList.innerHTML = '';
    expList.innerHTML = '';
    updatePreview();
  }

  // --- Event Listeners ---
  $('add-edu-btn').addEventListener('click', addEducation);
  $('add-exp-btn').addEventListener('click', addExperience);
  $('update-preview-btn').addEventListener('click', updatePreview);
  $('download-json-btn').addEventListener('click', downloadJSON);
  $('export-pdf-btn').addEventListener('click', exportPDF);
  $('clear-btn').addEventListener('click', clearAll);

  // Initialize with one block each
  addEducation();
  addExperience();
  updatePreview();
});
