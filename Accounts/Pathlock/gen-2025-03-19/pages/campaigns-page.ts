import { Page, Locator, expect } from '@playwright/test';

export class CampaignsPage {
  readonly page: Page;
  readonly exportButton: Locator;
  readonly scheduleReportOption: Locator;
  readonly screenNameInputSelector: string;
  readonly screenNameInput: Locator;
  readonly saveButton: Locator;
  readonly saveNotificationSelector: string;
  readonly openMenuButton: Locator;
  readonly complianceMenuItem: Locator;
  readonly adminMenuItem: Locator;
  readonly reportingMenuItem: Locator;
  readonly scheduledReportsMenuItem: Locator;

  constructor(page: Page) {
    this.page = page;
    this.exportButton = page.locator('#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_SystemMenun1 > table > tbody > tr > td:nth-child(1) > a');
    this.scheduleReportOption = page.locator('#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_SystemMenun165 > td > table > tbody > tr > td > a')
    this.screenNameInputSelector = '#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_ReportSchedule1_TabContainer_ScheduleInfo_txtScreenName';
    this.screenNameInput = page.locator('#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_ReportSchedule1_TabContainer_ScheduleInfo_txtScreenName');
    // FIXME: There is BUG on https://flex-qa-plc.stage.pathlockgrc.com/App/Campaigns
    // The ID selector `#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_SaveReportSchedule`
    //    ...is not unique!
    // IDs must be unique within a page
    // Please inform the relevant product team
    // FIXME: Thnere is another BUG with HTML/CSS selectors defined
    // Do not use $ in the `id` or `name` as it is used as an attribute post-fix selector
    // Example const element = page.locator('div[class$="value"]');
    // Therefore, when the `id` or `name` contains `$`, it will not be able to find the element
    // ..as the underlying parser gets confused with the `$` in the selector
    // FIXME: Use data-attributes `data-test-id` for unique identification for E2E tests
    // Example: <button data-test-id="save-button">Save</button>
    this.saveButton = page.locator('input:not([tabindex="-1"])#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_ProfileTailorMenuPanel1_SaveReportSchedule');
    this.saveNotificationSelector = '#ctl00_ctl00_ctl00_ctl00_ProfileTailorHeader1_MessageBoxArea > div';
    this.openMenuButton = page.locator('#ctl00_ctl00_ctl00_ctl00_div2 > ul > li:nth-child(1) > a > span.sr-only');
    this.complianceMenuItem = page.locator('#ctl00_ctl00_ctl00_ctl00_TreeView1t156');
    this.adminMenuItem = page.locator('#ctl00_ctl00_ctl00_ctl00_TreeView1t179');
    this.reportingMenuItem = page.locator('#ctl00_ctl00_ctl00_ctl00_TreeView1t218');
    this.scheduledReportsMenuItem = page.locator('#ctl00_ctl00_ctl00_ctl00_TreeView1t220');
  }

  async hoverOverExport() {
    await this.exportButton.hover();
  }

  async clickScheduleReport() {
    await this.scheduleReportOption.click();
    await this.page.waitForSelector(this.screenNameInputSelector);
  }

  async enterReportName(name: string) {
    await this.screenNameInput.fill(name);
  }

  async saveReport() {
    await this.saveButton.scrollIntoViewIfNeeded();
    await this.saveButton.click();
    await this.page.waitForSelector(this.saveNotificationSelector);
  }

  async openMenu() {
    await this.openMenuButton.click();
  }

  async navigateToAdmin() {
    await this.complianceMenuItem.click();
    await this.adminMenuItem.click();
  }

  async navigateToReporting() {
    await this.reportingMenuItem.click();
  }

  async navigateToScheduledReports() {
    await this.scheduledReportsMenuItem.click();
    await this.page.waitForURL('/App/Schedules/List.aspx');
  }
}
