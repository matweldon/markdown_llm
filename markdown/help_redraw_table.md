# %User

This is the client-side code in 'app.js' on my single-page web app:
```javascript
document.addEventListener('DOMContentLoaded', function() {

    const fileInput = document.getElementById('csv-file');

    const jobTable = $('#job-table').DataTable({
        select: 'single',
        columns: [
            { data: 'id' },
            { data: 'title' },
            { data: 'description' }
        ]
    });
    // const jobListBody = document.getElementById('job-list-body');
    const jobDetailsContent = document.getElementById('job-details-content');

    let jobs = [];
    let socResultsData = {};
    const socResultsDataTable = $('#soc-results-table').DataTable({
        columns: [
            { data: 'id', title: 'SOC code' },
            { data: 'description', title: 'Description' },
            { data: 'distance', title: 'Distance' }
        ],
        order: [[2, 'asc']],
        pageLength: 5,
        lengthChange: false,
        searching: false
    });

    function loadSavedData() {
        const savedData = localStorage.getItem('jobsData');
        const savedSocResults = localStorage.getItem('socResultsData');
        if (savedData) {
            jobs = JSON.parse(savedData);
            updateJobTable(jobs);
        }
        if (savedSocResults) {
            socResultsData = JSON.parse(savedSocResults);
        }
    }

    loadSavedData();

    fileInput.addEventListener('change',handleFileSelect);

    function handleFileSelect(event) {
        localStorage.removeItem('jobsData');
        localStorage.removeItem('selectedJobId');
        const file = event.target.files[0];
        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            error: function(error, file) { console.log("Error", error, file) },
            complete: function(results, file) {
                console.log("Complete");
                console.log(results.data);
                jobs = results.data.map((row, index) => ({
                    id: index + 1,
                    title: row.title.trim(),
                    description: row.description.trim(),
                    wage: parseFloat(row.wage.trim()),
                    supervision: row.supervision.trim(),
                    employer: row.employer.trim(),
                }));
                console.log(jobs);

                // Save jobs data to localStorage
                localStorage.setItem('jobsData', JSON.stringify(jobs));
                updateJobTable(jobs);

                // Send jobs data to backend for SOC code prediction
                fetchSocResults(jobs);
            }
        });
    }


    function fetchSocResults(jobsData) {
        fetch('/predict_soc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jobsData),
        })
        .then(response => response.json())
        .then(data => {
            console.log(JSON.stringify(data));
            socResultsData = data;
            localStorage.setItem('socResultsData', JSON.stringify(data));
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function updateJobTable(jobsData) {
        jobTable.clear();
        jobTable.rows.add(jobsData.map(job => ({
            id: job.id,
            title: job.title,
            description: job.description
        }))).draw();
        
        $('#job-table tbody').off('click', 'tr').on('click', 'tr', function() {
            const rowData = jobTable.row(this).data();
            localStorage.setItem('selectedJobId', rowData.id);
            const fullJobData = jobs.find(job => job.id === rowData.id);
            showJobDetails(fullJobData);
        });

        // Restore selected row
        const selectedJobId = localStorage.getItem('selectedJobId');
        if (selectedJobId) {
            const row = jobTable.row((idx, data) => data.id === parseInt(selectedJobId));
            if (row.length) {
                row.select();
                const fullJobData = jobs.find(job => job.id === parseInt(selectedJobId));
                showJobDetails(fullJobData);
            }
        }
    }

    function showJobDetails(job) {
        jobDetailsContent.innerHTML = `
            <h2>${job.title}</h2>
            <p><strong>Description:</strong> ${job.description}</p>
            <p><strong>Wage:</strong> ${job.wage.toLocaleString('en-UK', { style: 'currency', currency: 'GBP' })}</p>
            <p><strong>Supervisory responsibilities:</strong> ${job.supervision}</p>
            <p><strong>Employer:</strong> ${job.employer}</p>

        `;
        showSocResults(job.id);
    }

    function showSocResults(jobId) {
        const results = socResultsData.find(item => item.id === jobId);
        if (results && results.response) {
            results.response.forEach(row => {
                row.distance = parseFloat(row.distance).toFixed(2);
            })
            socResultsDataTable.clear().rows.add(results.response).draw();
        } else {
            socResultsDataTable.clear().draw();
        }
    }
});
```

Fetch takes a few seconds to complete. How do I trigger a redraw of `socResultsDataTable` when the fetch completes?

# %Assistant

To trigger a redraw of the `socResultsDataTable` when the fetch completes, you can modify your `fetchSocResults` function to include the redraw logic. Here's how you can do it:

1. First, create a new function to update the SOC results table:

```javascript
function updateSocResultsTable() {
    const selectedJobId = localStorage.getItem('selectedJobId');
    if (selectedJobId) {
        showSocResults(parseInt(selectedJobId));
    }
}
```

2. Then, modify your `fetchSocResults` function to call this new function after the data is received and stored:

```javascript
function fetchSocResults(jobsData) {
    fetch('/predict_soc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobsData),
    })
    .then(response => response.json())
    .then(data => {
        console.log(JSON.stringify(data));
        socResultsData = data;
        localStorage.setItem('socResultsData', JSON.stringify(data));
        updateSocResultsTable(); // Add this line
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
```

3. Optionally, you might want to show a loading indicator while the fetch is in progress. You can add this at the beginning of the `fetchSocResults` function:

```javascript
function fetchSocResults(jobsData) {
    // Show loading indicator
    socResultsDataTable.clear().draw();
    socResultsDataTable.row.add({id: 'Loading...', description: 'Please wait', distance: ''}).draw();

    fetch('/predict_soc', {
        // ... rest of the function
    })
}
```

These changes will ensure that the SOC results table is updated as soon as the fetch completes. If a job is already selected when the fetch completes, its SOC results will be immediately displayed.

Remember to add the new `updateSocResultsTable` function to your code. This approach maintains the separation of concerns, keeping the fetch logic separate from the display logic, while ensuring that the display is updated when new data is available.