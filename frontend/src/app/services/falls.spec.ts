import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { FallsService } from './falls';

describe('FallsService', () => {
  let service: FallsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient()]
    });

    service = TestBed.inject(FallsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});