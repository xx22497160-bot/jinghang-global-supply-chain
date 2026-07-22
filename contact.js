(function () {
  "use strict";

  var form = document.getElementById("project-enquiry-form");
  if (!form) {
    return;
  }

  var submitButton = form.querySelector('button[type="submit"]');
  var status = document.getElementById("form-status");
  var turnstileContainer = document.getElementById("turnstile-container");
  var turnstileToken = "";
  var turnstileWidgetId = null;
  var submitting = false;
  var preserveSuccessStatus = false;

  function setStatus(message, isError) {
    if (!status) {
      return;
    }
    status.classList.toggle("form-status-error", Boolean(isError));
    status.classList.toggle("form-status-success", Boolean(message) && !isError);
    status.textContent = message || "";
  }

  function setSubmitting(value) {
    submitting = value;
    form.setAttribute("aria-busy", value ? "true" : "false");
    if (submitButton) {
      submitButton.disabled = value || !turnstileToken;
      submitButton.textContent = value ? "Sending..." : "Send Project Enquiry";
    }
  }

  function loadTurnstileScript() {
    if (window.turnstile) {
      return Promise.resolve();
    }

    return new Promise(function (resolve, reject) {
      var existing = document.getElementById("turnstile-api");
      if (existing) {
        existing.addEventListener("load", resolve, { once: true });
        existing.addEventListener("error", reject, { once: true });
        return;
      }

      var script = document.createElement("script");
      script.id = "turnstile-api";
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      script.async = true;
      script.defer = true;
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener("error", reject, { once: true });
      document.head.appendChild(script);
    });
  }

  function resetTurnstile() {
    turnstileToken = "";
    if (window.turnstile && turnstileWidgetId !== null) {
      window.turnstile.reset(turnstileWidgetId);
    }
    setSubmitting(false);
  }

  function initialiseSecureForm() {
    if (!turnstileContainer || !submitButton) {
      setStatus("The secure form is temporarily unavailable. Please email hello@jinghangsc.com.", true);
      return;
    }

    Promise.all([
      fetch("/api/contact-config", {
        method: "GET",
        headers: { Accept: "application/json" },
        credentials: "same-origin",
        cache: "no-store"
      }).then(function (response) {
        if (!response.ok) {
          throw new Error("Configuration unavailable");
        }
        return response.json();
      }),
      loadTurnstileScript()
    ]).then(function (results) {
      var config = results[0];
      if (!config.siteKey || !window.turnstile) {
        throw new Error("Security check unavailable");
      }

      turnstileWidgetId = window.turnstile.render(turnstileContainer, {
        sitekey: config.siteKey,
        action: "contact_enquiry",
        theme: "light",
        callback: function (token) {
          turnstileToken = token;
          if (!submitting) {
            submitButton.disabled = false;
          }
          if (!preserveSuccessStatus) {
            setStatus("Security check complete. You can send your enquiry.", false);
          }
        },
        "expired-callback": function () {
          turnstileToken = "";
          submitButton.disabled = true;
          if (!preserveSuccessStatus) {
            setStatus("The security check expired. Please complete it again.", true);
          }
        },
        "error-callback": function () {
          turnstileToken = "";
          submitButton.disabled = true;
          if (!preserveSuccessStatus) {
            setStatus("The security check could not load. Please retry or email us directly.", true);
          }
        }
      });
    }).catch(function () {
      submitButton.disabled = true;
      setStatus("The secure form is temporarily unavailable. Please email hello@jinghangsc.com.", true);
    });
  }

  function fieldValue(name) {
    var field = form.elements.namedItem(name);
    return field && "value" in field ? String(field.value).trim() : "";
  }

  function selectedServices() {
    return Array.prototype.slice.call(form.querySelectorAll('input[name="service"]:checked')).map(function (field) {
      return String(field.value).trim();
    });
  }

  function buildPayload() {
    var confirmation = form.querySelector('input[name="information_confirmation"]');
    return {
      full_name: fieldValue("full_name"),
      company_name: fieldValue("company_name"),
      work_email: fieldValue("work_email"),
      country_and_time_zone: fieldValue("country_and_time_zone"),
      company_website: fieldValue("company_website"),
      project_stage: fieldValue("project_stage"),
      product_and_project_details: fieldValue("product_and_project_details"),
      supplier_quantity_and_cargo: fieldValue("supplier_quantity_and_cargo"),
      origin_city: fieldValue("origin_city"),
      destination: fieldValue("destination"),
      sensitive_cargo_details: fieldValue("sensitive_cargo_details"),
      services: selectedServices(),
      target_date: fieldValue("target_date"),
      messaging_contact: fieldValue("messaging_contact"),
      information_confirmation: confirmation && confirmation.checked ? "confirmed" : "",
      website_url: fieldValue("website_url"),
      turnstile_token: turnstileToken
    };
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    if (submitting || !form.reportValidity()) {
      return;
    }
    if (!turnstileToken) {
      setStatus("Please complete the security check before sending.", true);
      return;
    }

    preserveSuccessStatus = false;
    setStatus("Sending your enquiry securely...", false);
    setSubmitting(true);

    fetch(form.action, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      credentials: "same-origin",
      body: JSON.stringify(buildPayload())
    }).then(function (response) {
      return response.json().catch(function () {
        return { ok: false, message: "The server returned an unexpected response." };
      }).then(function (payload) {
        return { response: response, payload: payload };
      });
    }).then(function (result) {
      if (!result.response.ok || !result.payload.ok) {
        throw new Error(result.payload.message || "We could not send the enquiry.");
      }

      form.reset();
      preserveSuccessStatus = true;
      setStatus(result.payload.message || "Thank you. Your enquiry has been sent.", false);
    }).catch(function (error) {
      setStatus((error && error.message ? error.message : "We could not send the enquiry.") + " You can also email hello@jinghangsc.com.", true);
    }).finally(function () {
      resetTurnstile();
    });
  });

  form.addEventListener("input", function () {
    if (!preserveSuccessStatus) {
      return;
    }
    preserveSuccessStatus = false;
    setStatus(turnstileToken ? "Security check complete. You can send your enquiry." : "", false);
  });

  initialiseSecureForm();
}());
