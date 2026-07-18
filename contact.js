(function () {
  "use strict";

  var form = document.getElementById("project-enquiry-form");
  if (!form) {
    return;
  }

  var submitButton = form.querySelector('button[type="submit"]');
  var status = document.getElementById("form-status");
  var recipient = form.getAttribute("data-email-recipient") || "hello@jinghangsc.com";

  function textValue(data, name) {
    var value = data.get(name);
    return value ? String(value).trim() : "Not provided";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    var data = new FormData(form);
    var services = data.getAll("service").map(function (value) {
      return String(value).trim();
    }).filter(Boolean);
    var fullName = textValue(data, "full_name");
    var company = textValue(data, "company_name");
    var subjectName = company !== "Not provided" ? company : fullName;
    var subject = "New website project enquiry - " + subjectName;
    var body = [
      "Hello Jinghang SC team,",
      "",
      "I would like to discuss the following project.",
      "",
      "CONTACT",
      "Full name: " + fullName,
      "Company: " + company,
      "Work email: " + textValue(data, "work_email"),
      "Country / time zone: " + textValue(data, "country_and_time_zone"),
      "Company website: " + textValue(data, "company_website"),
      "Phone / WhatsApp / WeChat: " + textValue(data, "messaging_contact"),
      "",
      "PROJECT",
      "Current stage: " + textValue(data, "project_stage"),
      "Product and project details: " + textValue(data, "product_and_project_details"),
      "Suppliers, quantity, and cargo details: " + textValue(data, "supplier_quantity_and_cargo"),
      "Origin city: " + textValue(data, "origin_city"),
      "Destination city and postal code: " + textValue(data, "destination"),
      "Sensitive or special cargo details: " + textValue(data, "sensitive_cargo_details"),
      "Support requested: " + (services.length ? services.join(", ") : "Not specified"),
      "Target shipment or launch date: " + textValue(data, "target_date"),
      "",
      "I confirm that the information above is accurate to the best of my knowledge.",
      ""
    ].join("\n");
    var mailtoUrl = "mailto:" + recipient + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);

    if (status) {
      status.classList.remove("form-status-error");
    }

    if (mailtoUrl.length > 7000) {
      if (status) {
        status.classList.add("form-status-error");
        status.textContent = "This brief is too long for reliable email preparation. Keep this page open and copy the details into a new email to " + recipient + ".";
      }
      return;
    }

    if (status) {
      status.textContent = "Your email application should open now. Review the prepared message and choose Send.";
    }

    window.location.assign(mailtoUrl);
  });

  if (submitButton) {
    submitButton.disabled = false;
  }
}());
