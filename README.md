# Mansico Meta Integration

<div align="center">
    <img src="https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/4080cbd5-6f5f-48fe-877d-e28e5e795bf8" height="128">
    <h2>Seamlessly Sync Facebook Leads with ERPNext</h2>
</div>

**Mansico Meta Integration** is an open-source application designed to automate the synchronization of Facebook leads with ERPNext. When clients fill out Facebook Ads instant forms, the app automatically fetches the newly created leads and generates corresponding entries in ERPNext's **Lead** doctype. Additionally, when the Lead Status is updated in ERPNext, the new status is sent back to the Meta Pixel for real-time tracking and analytics.

---

## Key Features

- **Automated Lead Sync**: Fetches new leads from Facebook Ads instant forms and creates them in ERPNext automatically.
- **Real-Time Status Updates**: Sends updated lead statuses from ERPNext back to the Meta Pixel for enhanced tracking.
- **Customizable Sync Frequency**: Configure how often the app fetches new leads (e.g., every 15 minutes, hourly, etc.).
- **Seamless Integration**: Works with Meta Business Accounts, Marketing API, and ERPNext for a smooth setup process.
- **Open-Source and Extendable**: Fully customizable to meet specific business needs.

---

## Installation

### Frappe Cloud (One-Click Install)
Great new now available for FREE on [Frappe Cloud Marketplace](https://frappecloud.com/marketplace/apps/mansico_meta_integration). Stay tuned for updates!

### Self-Hosting

1. **Clone the App Repository**:
   ```bash
   bench get-app https://github.com/splinter-NGoH/mansico_meta_integration.git
   ```

2. **Install the App**:
   ```bash
   bench --site [your.site.name] install-app mansico_meta_integration
   ```

3. **Run Database Migrations**:
   ```bash
   bench --site [your.site.name] migrate
   ```

---

## Facebook Requirements

To use this integration, you need the following:

1. **Meta Business Account**:
   - If you don’t already have one, create a [Meta Business Account](https://www.facebook.com/business/help/1710077379203657?id=180505742745347).

2. **Meta App**:
   - Create a Meta App to access the Marketing API. Follow the steps below:
     ![Meta App Creation](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/70138d92-07c2-4e05-8a6b-a408854a3900)

3. **Marketing API Setup**:
   - Enable the Marketing API for your app.
     ![Marketing API Setup](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/7b81826e-1ffe-46e7-9954-b7b38d522f8e)

4. **Access Token for System User**:
   - Go to **Meta Settings > Users > System Users** and add a new user or use an existing one.
   - Assign the necessary permissions (`leads_retrieval`, `manage_pages`, `ads_management`, `business_management`).
   - Generate an access token and copy it.
     ![Access Token Generation](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/273d3c1b-766e-4bab-9b2e-fca3213b916b)

5. **Pixel ID and Pixel Access Token**:
   - Go to **Events Manager** in your Meta Business Account.
   - Locate your Pixel ID and generate a Pixel Access Token.
     ![Pixel Setup](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/8dd287ee-4903-4285-9ba4-2808a7827aa9)

---

## Configuration in ERPNext

1. **Meta Facebook Settings**:
   - Paste the **Access Token** in the respective field.
   - Set the **API URL** (e.g., `https://graph.facebook.com`) and **Graph API Version** (e.g., `v16.0`).
     ![Meta Settings](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/d802a857-7807-4cd6-ae4e-cef10466816a)

2. **Page ID Doctype**:
   - Add your Facebook Page Name, Page ID, Pixel ID, and Pixel Access Token.
     ![Page ID Setup](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/164bbb69-9539-4579-a7bf-568d91c74bcc)

3. **Sync New Lead**:
   - Create a new sync job and configure the **Event Frequency** (e.g., every 15 minutes).
   - Ensure the **Lead Status Mapping** is correctly set up.
     ![Sync Setup](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/4cbc636a-181b-483d-9e25-7bc15cf9c5dd)

4. **Schedule Job**:
   - The sync job will be queued. You can manually execute it from **Schedule Job Type**.
     ![Schedule Job](https://github.com/splinter-NGoH/mansico_meta_integration/assets/73743592/89f8893d-165e-4700-a939-76e8b5e9fa04)

5. **Verify Leads**:
   - Check the **Lead** doctype to confirm that new leads have been created.

---

## Support the Project

If you find this project useful, consider supporting its development! Your contributions help maintain and improve the app.

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://paypal.me/AhmedMansyArt?country.x=EG&locale.x=en_US)

---

## Dependencies

- [Frappe Framework](https://github.com/frappe/frappe)
- [ERPNext](https://github.com/frappe/erpnext)

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/splinter-NGoH/mansico_meta_integration/blob/main/LICENSE) file for details.

---

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## Support

For support or questions, open an issue on the [GitHub repository](https://github.com/splinter-NGoH/mansico_meta_integration) or contact the maintainers.

---

## Important Note

This app is actively maintained, and new updates will be released regularly. Don’t forget to ⭐️ the repository to show your support! Pull requests from developers are highly encouraged.

Cheers from Mansy! 🚀
