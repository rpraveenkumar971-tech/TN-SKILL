// =========================================================
// PocketSmart AI Frontend JavaScript
// =========================================================


// ---------------------------------------------------------
// Helper
// ---------------------------------------------------------

function $(selector) {
    return document.querySelector(selector);
}


// ---------------------------------------------------------
// HTML escaping
// ---------------------------------------------------------

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ---------------------------------------------------------
// Convert form to JSON object
// ---------------------------------------------------------

function formToObject(form) {

    const data = {};

    const formData = new FormData(form);

    formData.forEach((value, key) => {

        if (key === "image") {
            return;
        }

        data[key] = value;
    });


    // Checkbox values
    for (const element of form.elements) {

        if (
            element.type === "checkbox"
        ) {

            data[element.name] =
                element.checked;
        }
    }


    // Numeric fields
    const numericFields = [
        "total_budget",
        "num_lights",
        "num_fans",
        "num_furniture",
        "num_dining_tables",
        "num_guests"
    ];


    numericFields.forEach(
        field => {

            if (
                field in data
            ) {

                data[field] =
                    Number(
                        data[field]
                    );
            }
        }
    );


    return data;
}


// ---------------------------------------------------------
// Currency formatting
// ---------------------------------------------------------

function money(value) {

    const number =
        Number(value || 0);

    return number.toLocaleString(
        "en-IN",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    );
}


// ---------------------------------------------------------
// Shopping links
// ---------------------------------------------------------

function renderLinks(links) {

    if (!links) {
        return "";
    }

    return Object.entries(
        links
    )
        .map(
            ([name, url]) => `
                <a
                    href="${escapeHtml(url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="shopping-link"
                >
                    ${escapeHtml(name)}
                </a>
            `
        )
        .join("");
}


// ---------------------------------------------------------
// Budget recommendation
// ---------------------------------------------------------

function renderBudgetResult(data) {

    let html = `

        <div class="result-header">

            <span class="pill">
                AI Recommendation
            </span>

            <h2>
                Personalized Budget Plan
            </h2>

            <div class="budget-summary">

                <div>
                    <span>
                        Total Budget
                    </span>

                    <strong>
                        ₹${money(data.total_budget)}
                    </strong>
                </div>

                <div>
                    <span>
                        Estimated Spend
                    </span>

                    <strong>
                        ₹${money(data.spent_amount)}
                    </strong>
                </div>

                <div>
                    <span>
                        Remaining
                    </span>

                    <strong>
                        ₹${money(data.remaining_budget)}
                    </strong>
                </div>

            </div>

        </div>
    `;


    const categories =
        data.budget_breakdown || [];


    categories.forEach(
        category => {

            html += `

                <div class="recommendation-category">

                    <div class="category-header">

                        <h3>
                            ${escapeHtml(
                                category.category
                            )}
                        </h3>

                        <span>
                            ₹${money(
                                category.allocation
                            )}
                        </span>

                    </div>
            `;


            const items =
                category.items || [];


            items.forEach(
                item => {

                    html += `

                        <div class="recommendation-item">

                            <div>

                                <h4>
                                    ${escapeHtml(
                                        item.name
                                    )}
                                </h4>

                                <p>
                                    ${escapeHtml(
                                        item.description
                                    )}
                                </p>

                                <div class="item-meta">

                                    ₹${money(
                                        item.estimated_price
                                    )}

                                    ×

                                    ${item.quantity}

                                </div>

                            </div>

                            <div class="shopping-links">

                                ${renderLinks(
                                    item.shopping_links
                                )}

                            </div>

                        </div>
                    `;
                }
            );


            html += `
                </div>
            `;
        }
    );


    if (
        data.venue_suggestions &&
        data.venue_suggestions.length
    ) {

        html += `

            <div class="recommendation-category">

                <h3>
                    Venue Suggestions
                </h3>
        `;


        data.venue_suggestions.forEach(
            venue => {

                html += `

                    <div class="recommendation-item">

                        <h4>
                            ${escapeHtml(
                                venue.name
                            )}
                        </h4>

                        <p>
                            Type:
                            ${escapeHtml(
                                venue.type || ""
                            )}
                        </p>

                        <p>
                            Capacity:
                            ${escapeHtml(
                                venue.capacity || ""
                            )}
                        </p>

                        <div class="shopping-links">

                            ${renderLinks(
                                venue.search_links
                            )}

                        </div>

                    </div>
                `;
            }
        );


        html += `
            </div>
        `;
    }


    if (
        data.additional_suggestions &&
        data.additional_suggestions.length
    ) {

        html += `

            <div class="suggestions">

                <h3>
                    Suggestions
                </h3>

                <ul>
        `;


        data.additional_suggestions.forEach(
            suggestion => {

                html += `
                    <li>
                        ${escapeHtml(
                            suggestion
                        )}
                    </li>
                `;
            }
        );


        html += `
                </ul>
            </div>
        `;
    }


    return html;
}


// ---------------------------------------------------------
// Jewelry result
// ---------------------------------------------------------

function renderJewelryResult(data) {

    let html = `

        <div class="result-header">

            <span class="pill">
                AI Recommendation
            </span>

            <h2>
                Jewelry Recommendations
            </h2>

            <div class="budget-summary">

                <div>
                    <span>
                        Budget
                    </span>

                    <strong>
                        ₹${money(
                            data.total_budget
                        )}
                    </strong>
                </div>

                <div>
                    <span>
                        Estimated Spend
                    </span>

                    <strong>
                        ₹${money(
                            data.spent_amount
                        )}
                    </strong>
                </div>

                <div>
                    <span>
                        Remaining
                    </span>

                    <strong>
                        ₹${money(
                            data.remaining_budget
                        )}
                    </strong>
                </div>

            </div>

        </div>
    `;


    if (
        data.outfit_analysis
    ) {

        const outfit =
            data.outfit_analysis;


        html += `

            <div class="outfit-analysis">

                <h3>
                    Outfit Analysis
                </h3>

                <p>
                    <strong>
                        Style:
                    </strong>

                    ${escapeHtml(
                        outfit.style ||
                        "Not available"
                    )}
                </p>

                <p>
                    <strong>
                        Formality:
                    </strong>

                    ${escapeHtml(
                        outfit.formality ||
                        "Not available"
                    )}
                </p>

                <p>
                    <strong>
                        Colors:
                    </strong>

                    ${escapeHtml(
                        (
                            outfit.colors ||
                            []
                        ).join(", ")
                        ||
                        "Not available"
                    )}
                </p>

            </div>
        `;
    }


    const items =
        data.jewelry_recommendations ||
        [];


    items.forEach(
        item => {

            html += `

                <div class="recommendation-item">

                    <h3>
                        ${escapeHtml(
                            item.item_type
                        )}
                    </h3>

                    <p>
                        ${escapeHtml(
                            item.description
                        )}
                    </p>

                    <p>
                        <strong>
                            Style:
                        </strong>

                        ${escapeHtml(
                            item.style
                        )}
                    </p>

                    <p class="price">

                        ₹${money(
                            item.estimated_price
                        )}

                    </p>

                    <div class="shopping-links">

                        ${renderLinks(
                            item.shopping_links
                        )}

                    </div>

                </div>
            `;
        }
    );


    if (
        data.additional_suggestions &&
        data.additional_suggestions.length
    ) {

        html += `

            <div class="suggestions">

                <h3>
                    Suggestions
                </h3>

                <ul>
        `;


        data.additional_suggestions.forEach(
            suggestion => {

                html += `
                    <li>
                        ${escapeHtml(
                            suggestion
                        )}
                    </li>
                `;
            }
        );


        html += `
                </ul>
            </div>
        `;
    }


    return html;
}


// ---------------------------------------------------------
// Submit JSON planner
// ---------------------------------------------------------

async function submitPlanner(
    form,
    endpoint
) {

    const result =
        document.querySelector(
            "#result"
        );


    if (!result) {
        return;
    }


    result.innerHTML = `

        <div class="loading">

            <div class="spinner"></div>

            <p>
                AI is preparing your
                personalized recommendation...
            </p>

        </div>
    `;


    try {

        const response =
            await fetch(
                endpoint,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        formToObject(form)
                    )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Request failed."
            );
        }


        result.innerHTML =
            renderBudgetResult(
                data
            );

        result.scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        result.innerHTML = `

            <div class="error-box">

                <strong>
                    Error
                </strong>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}


// =========================================================
// Home form
// =========================================================

const homeForm =
    document.querySelector(
        "#homeForm"
    );


if (homeForm) {

    homeForm.addEventListener(
        "submit",
        event => {

            event.preventDefault();

            submitPlanner(
                homeForm,
                "/api/home-budget"
            );
        }
    );
}


// =========================================================
// Party form
// =========================================================

const partyForm =
    document.querySelector(
        "#partyForm"
    );


if (partyForm) {

    partyForm.addEventListener(
        "submit",
        event => {

            event.preventDefault();

            submitPlanner(
                partyForm,
                "/api/party-budget"
            );
        }
    );
}


// =========================================================
// Jewelry form
// =========================================================

const jewelryForm =
    document.querySelector(
        "#jewelryForm"
    );


if (jewelryForm) {

    jewelryForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const result =
                document.querySelector(
                    "#result"
                );


            result.innerHTML = `

                <div class="loading">

                    <div class="spinner"></div>

                    <p>
                        Preparing jewelry
                        recommendations...
                    </p>

                </div>
            `;


            try {

                const formData =
                    new FormData(
                        jewelryForm
                    );


                const response =
                    await fetch(
                        "/api/jewelry-budget",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Request failed."
                    );
                }


                result.innerHTML =
                    renderJewelryResult(
                        data
                    );


                result.scrollIntoView({
                    behavior: "smooth"
                });


            } catch (error) {

                result.innerHTML = `

                    <div class="error-box">

                        <strong>
                            Error
                        </strong>

                        <p>
                            ${escapeHtml(
                                error.message
                            )}
                        </p>

                    </div>
                `;
            }
        }
    );
}


// =========================================================
// Register
// =========================================================

const registerForm =
    document.querySelector(
        "#registerForm"
    );


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const message =
                document.querySelector(
                    "#msg"
                );


            try {

                const response =
                    await fetch(
                        "/register",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify(
                                formToObject(
                                    registerForm
                                )
                            )
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Registration failed."
                    );
                }


                message.className =
                    "message success";

                message.textContent =
                    "Account created successfully. Redirecting to login...";


                setTimeout(
                    () => {
                        window.location =
                            "/login";
                    },
                    1000
                );


            } catch (error) {

                message.className =
                    "message error";

                message.textContent =
                    error.message;
            }
        }
    );
}


// =========================================================
// Login
// =========================================================

const loginForm =
    document.querySelector(
        "#loginForm"
    );


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const message =
                document.querySelector(
                    "#msg"
                );


            try {

                const formData =
                    new URLSearchParams();


                formData.set(
                    "username",
                    loginForm.username.value
                );


                formData.set(
                    "password",
                    loginForm.password.value
                );


                const response =
                    await fetch(
                        "/token",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/x-www-form-urlencoded"
                            },

                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Login failed."
                    );
                }


                window.location =
                    "/dashboard";


            } catch (error) {

                message.className =
                    "message error";

                message.textContent =
                    error.message;
            }
        }
    );
}


// =========================================================
// History
// =========================================================

const historyContainer =
    document.querySelector(
        "#history"
    );


if (historyContainer) {

    loadHistory();
}


async function loadHistory() {

    try {

        const response =
            await fetch(
                "/api/history"
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load history."
            );
        }


        const history =
            data.history || [];


        if (!history.length) {

            historyContainer.innerHTML = `

                <div class="empty-result">

                    <div>
                        📋
                    </div>

                    <h2>
                        No recommendations yet
                    </h2>

                    <p>
                        Create your first budget
                        recommendation.
                    </p>

                </div>
            `;

            return;
        }


        historyContainer.innerHTML =
            history.map(
                item => `

                    <div
                        class="history-item"
                        data-id="${escapeHtml(
                            item.id
                        )}"
                    >

                        <div>

                            <span class="history-type">

                                ${escapeHtml(
                                    item.type
                                        .toUpperCase()
                                )}

                            </span>

                            <h3>
                                Budget Plan
                            </h3>

                            <p>
                                ${escapeHtml(
                                    item.summary
                                )}
                            </p>

                            <small>
                                ${new Date(
                                    item.timestamp
                                ).toLocaleString()}
                            </small>

                        </div>

                        <button
                            class="btn small"
                            onclick="viewHistory('${escapeHtml(item.id)}')"
                        >
                            View
                        </button>

                    </div>
                `
            ).join("");


    } catch (error) {

        historyContainer.innerHTML = `

            <div class="error-box">

                ${escapeHtml(
                    error.message
                )}

            </div>
        `;
    }
}


// ---------------------------------------------------------
// History detail
// ---------------------------------------------------------

async function viewHistory(id) {

    try {

        const response =
            await fetch(
                `/api/history/${encodeURIComponent(id)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load recommendation."
            );
        }


        const result =
            document.querySelector(
                "#history"
            );


        if (
            data.type === "jewelry"
        ) {

            result.innerHTML = `

                <button
                    class="btn secondary"
                    onclick="loadHistory()"
                >
                    ← Back to History
                </button>

                <div class="result-card history-detail">

                    ${renderJewelryResult(
                        data.full_result
                    )}

                </div>
            `;

        } else {

            result.innerHTML = `

                <button
                    class="btn secondary"
                    onclick="loadHistory()"
                >
                    ← Back to History
                </button>

                <div class="result-card history-detail">

                    ${renderBudgetResult(
                        data.full_result
                    )}

                </div>
            `;
        }


        result.scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        alert(
            error.message
        );
    }
}