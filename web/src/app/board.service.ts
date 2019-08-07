import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BoardService {
  getURL = "http://127.0.0.1:5000/boards";
  postURL = "http://127.0.0.1:5000/plot";
  constructor(private httpclient:HttpClient){}

  getBoards(): Observable<String[]> {
    return <Observable<String[]>> this.httpclient.get(this.getURL);
  }
  postBoards(boards: String[]): Observable<Blob> {
    return this.httpclient.post(this.postURL,boards.join(","),{responseType:'blob'});
  }
}
