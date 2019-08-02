import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {ImageViewerModule } from 'angular-image-viewer';

import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    ImageViewerModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
