import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Analysis } from 'src/data/Analysis';
import { AnalysisWrapper } from 'src/data/AnalysisWrapper';

@Injectable({
  providedIn: 'root'
})
export class BoardService {
  getURL = "http://127.0.0.1:5000/boards";
  dataURL = "http://127.0.0.1:5000/data";
  imgURL = "http://127.0.0.1:5000/plot";
  constructor(private httpclient:HttpClient){}

  getBoards(): Observable<String[]> {
    return <Observable<String[]>> this.httpclient.get(this.getURL);
  }
  postData(boards: String[]): Observable<AnalysisWrapper> {
    return <Observable<AnalysisWrapper>> this.httpclient.post(this.dataURL,boards.join(","));
  }
  postImg(boards: String[]): Observable<Blob> {
    return <Observable<Blob>> this.httpclient.post(this.imgURL,boards.join(','),{responseType:'blob'});
  }
}
